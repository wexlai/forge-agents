import pytest

import forge_repo
from agent_fixtures import write_agent

README = "# Forge agents\n\nIntro.\n\n<!-- agents:start -->\nold table\n<!-- agents:end -->\n\n## After\n"


def test_render_index_sorts_by_id_then_folder_and_escapes(tmp_path):
    write_agent(tmp_path, folder="forge-test-strands-python", manifest={"id": "test", "name": "Forge Test"})
    write_agent(tmp_path, folder="forge-spec-strands-python", manifest={"description": "Notes | stories"})
    write_agent(tmp_path, folder="forge-spec-strands", manifest={"status": "deprecated"})
    assert forge_repo.render_index(tmp_path) == "\n".join(
        [
            "| Agent | Framework | Language | Status | Description |",
            "| --- | --- | --- | --- | --- |",
            "| [Forge Spec](forge-spec-strands/) | strands | python | deprecated | Turns notes into stories |",
            "| [Forge Spec](forge-spec-strands-python/) | strands | python | beta | Notes \\| stories |",
            "| [Forge Test](forge-test-strands-python/) | strands | python | beta | Turns notes into stories |",
        ]
    )


def test_render_index_with_no_agents(tmp_path):
    assert forge_repo.render_index(tmp_path).endswith("| _No agents yet_ | | | | |")


def test_replace_index_keeps_surrounding_text():
    out = forge_repo.replace_index(README, "TABLE")
    assert out == "# Forge agents\n\nIntro.\n\n<!-- agents:start -->\nTABLE\n<!-- agents:end -->\n\n## After\n"


def test_replace_index_needs_markers():
    with pytest.raises(ValueError, match="agents:start"):
        forge_repo.replace_index("# no markers\n", "TABLE")


def test_update_index_writes_then_reports_current(tmp_path):
    write_agent(tmp_path)
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    assert forge_repo.update_index(tmp_path, check=True) is False
    assert "old table" in (tmp_path / "README.md").read_text(encoding="utf-8")  # check mode does not write
    assert forge_repo.update_index(tmp_path) is False
    assert "[Forge Spec](forge-spec-strands-python/)" in (tmp_path / "README.md").read_text(encoding="utf-8")
    assert forge_repo.update_index(tmp_path, check=True) is True


def test_cli_index_check_fails_when_stale(tmp_path, capsys):
    write_agent(tmp_path)
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    assert forge_repo.main(["--root", str(tmp_path), "index", "--check"]) == 1
    assert "out of date" in capsys.readouterr().err
    assert forge_repo.main(["--root", str(tmp_path), "index"]) == 0
    assert forge_repo.main(["--root", str(tmp_path), "index", "--check"]) == 0


def test_cli_index_refuses_invalid_folders(tmp_path, capsys):
    write_agent(tmp_path, env=None)
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    assert forge_repo.main(["--root", str(tmp_path), "index"]) == 1
    assert ".env.example is missing" in capsys.readouterr().err


def test_cli_index_reports_missing_markers(tmp_path, capsys):
    write_agent(tmp_path)
    (tmp_path / "README.md").write_text("# no markers\n", encoding="utf-8")
    assert forge_repo.main(["--root", str(tmp_path), "index"]) == 1
    assert "agents:start" in capsys.readouterr().err
