import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import forge_repo
from agent_fixtures import write_agent


def git(root: Path, *args: str, date: str | None = None) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    if date:
        env |= {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=root, env=env, check=True, capture_output=True)


def three_agents(root: Path) -> None:
    write_agent(root)
    write_agent(root, folder="forge-test-strands-python", manifest={"id": "test"})
    write_agent(root, folder="forge-review-strands-python", manifest={"id": "review", "status": "deprecated"})


def test_select_folders_rules():
    folders = [Path("forge-a-strands"), Path("forge-b-strands")]
    assert forge_repo.select_folders(folders, None) == folders
    assert forge_repo.select_folders(folders, ["forge-b-strands/src/x.py"]) == [Path("forge-b-strands")]
    assert forge_repo.select_folders(folders, ["tools/forge_repo.py"]) == folders
    assert forge_repo.select_folders(folders, [".github/workflows/ci.yml"]) == folders
    assert forge_repo.select_folders(folders, ["templates/agent/README.md"]) == folders
    assert forge_repo.select_folders(folders, ["README.md", "docs/x.md"]) == []


def test_matrix_entries(tmp_path):
    write_agent(tmp_path)
    assert forge_repo.matrix(tmp_path) == [
        {
            "folder": "forge-spec-strands-python",
            "runtime": "python",
            "version": "3.12",
            "setup": "uv sync",
            "test": "uv run pytest",
            "example": "uv run forge-spec examples/a.input.txt",
        }
    ]


def test_matrix_skip_deprecated_and_agent_filter(tmp_path):
    three_agents(tmp_path)
    names = [e["folder"] for e in forge_repo.matrix(tmp_path, skip_deprecated=True)]
    assert names == ["forge-spec-strands-python", "forge-test-strands-python"]
    assert [e["folder"] for e in forge_repo.matrix(tmp_path, agent="forge-test-strands-python/")] == [
        "forge-test-strands-python"
    ]


def test_matrix_skips_invalid_manifest(tmp_path, capsys):
    write_agent(tmp_path)
    write_agent(tmp_path, folder="forge-bad-strands", manifest={"id": "bad", "runtime": {"python": 3.12}})
    assert [e["folder"] for e in forge_repo.matrix(tmp_path)] == ["forge-spec-strands-python"]
    assert "forge-bad-strands: skipped" in capsys.readouterr().err


def test_cli_matrix_changed_from_git(tmp_path, capsys):
    git(tmp_path, "init", "-b", "main")
    three_agents(tmp_path)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-m", "one")
    (tmp_path / "forge-test-strands-python" / "examples" / "demo.input.txt").write_text("changed", encoding="utf-8")
    git(tmp_path, "commit", "-am", "two")
    assert forge_repo.main(["--root", str(tmp_path), "matrix", "--changed-from", "HEAD~1"]) == 0
    out = capsys.readouterr().out.strip()
    assert "\n" not in out
    assert [e["folder"] for e in json.loads(out)] == ["forge-test-strands-python"]


def test_cli_matrix_unknown_agent(tmp_path, capsys):
    assert forge_repo.main(["--root", str(tmp_path), "matrix", "--agent", "forge-nope"]) == 1
    assert "no such agent folder" in capsys.readouterr().err


def test_cli_matrix_bad_ref(tmp_path, capsys):
    git(tmp_path, "init", "-b", "main")
    write_agent(tmp_path)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-m", "one")
    assert forge_repo.main(["--root", str(tmp_path), "matrix", "--changed-from", "no-such-ref"]) == 1
    assert "git diff failed" in capsys.readouterr().err


def test_stale_folders(tmp_path, capsys):
    git(tmp_path, "init", "-b", "main")
    three_agents(tmp_path)
    git(tmp_path, "add", "forge-spec-strands-python", "forge-review-strands-python")
    git(tmp_path, "commit", "-m", "old", date="2026-01-01T00:00:00+00:00")
    git(tmp_path, "add", "forge-test-strands-python")
    git(tmp_path, "commit", "-m", "new", date="2026-10-01T00:00:00+00:00")
    write_agent(tmp_path, folder="forge-data-strands-python", manifest={"id": "data"})  # never committed
    now = datetime(2026, 10, 12, tzinfo=timezone.utc).timestamp()
    assert forge_repo.stale_folders(tmp_path, days=120, now=now) == ["forge-spec-strands-python"]
    assert forge_repo.main(["--root", str(tmp_path), "stale", "--days", "100000"]) == 0
    assert capsys.readouterr().out == ""
