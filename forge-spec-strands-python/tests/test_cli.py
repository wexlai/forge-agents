import os

import pytest
from conftest import StubModel

from forge_spec.cli import main


@pytest.fixture
def notes(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("PM: ship the retry button\n", encoding="utf-8")
    return path


def test_markdown_to_stdout(notes, capsys, sample_payload):
    assert main([str(notes)], model=StubModel(sample_payload)) == 0
    assert capsys.readouterr().out.startswith("# Epic: Retry the questions you missed\n")


def test_jira_csv_to_file(notes, tmp_path, capsys, sample_payload):
    out = tmp_path / "out.csv"
    assert main([str(notes), "--format", "jira-csv", "--out", str(out)], model=StubModel(sample_payload)) == 0
    assert out.read_text(encoding="utf-8").startswith("Issue Id,Parent,Issue Type,Summary,Description\n")
    assert capsys.readouterr().out == ""


def test_missing_input_exits_2(tmp_path, capsys, sample_payload):
    assert main([str(tmp_path / "nope.txt")], model=StubModel(sample_payload)) == 2
    err = capsys.readouterr().err
    assert "file not found" in err and "Traceback" not in err


def test_unsupported_input_exits_2(tmp_path, capsys, sample_payload):
    path = tmp_path / "notes.docx"
    path.write_bytes(b"PK")
    assert main([str(path)], model=StubModel(sample_payload)) == 2
    assert "unsupported file type '.docx'" in capsys.readouterr().err


def test_missing_key_exits_2_before_any_model_call(notes, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("MODEL_PROVIDER", "openai")
    assert main([str(notes)]) == 2
    assert "needs OPENAI_API_KEY" in capsys.readouterr().err


def test_env_file_in_working_directory_is_read(notes, tmp_path, monkeypatch, capsys):
    # load_dotenv writes into os.environ; give it a throwaway copy so nothing leaks into other tests
    monkeypatch.setattr(os, "environ", {k: v for k, v in os.environ.items() if k != "MODEL_PROVIDER"})
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("MODEL_PROVIDER=groq\n", encoding="utf-8")
    assert main([str(notes)]) == 2
    assert "Unknown MODEL_PROVIDER 'groq'" in capsys.readouterr().err


def test_model_failure_exits_1_and_writes_nothing(notes, tmp_path, capsys):
    out = tmp_path / "out.md"
    assert main([str(notes), "--out", str(out)], model=StubModel(error=RuntimeError("upstream 500"))) == 1
    err = capsys.readouterr().err
    assert "generation failed" in err and "upstream 500" in err
    assert not out.exists()


def test_out_in_missing_directory_exits_2_before_any_model_call(notes, tmp_path, capsys, sample_payload):
    stub = StubModel(sample_payload)
    assert main([str(notes), "--out", str(tmp_path / "missing" / "spec.md")], model=stub) == 2
    assert stub.calls == []
    assert "directory does not exist" in capsys.readouterr().err


def test_out_that_is_a_directory_exits_2_before_any_model_call(notes, tmp_path, capsys, sample_payload):
    stub = StubModel(sample_payload)
    assert main([str(notes), "--out", str(tmp_path)], model=stub) == 2
    assert stub.calls == []
    assert "is a directory" in capsys.readouterr().err


def test_write_failure_keeps_the_result_on_stdout(notes, tmp_path, monkeypatch, capsys, sample_payload):
    out = tmp_path / "spec.md"

    def refuse(*args, **kwargs):
        raise PermissionError("read-only file system")

    monkeypatch.setattr(type(out), "write_text", refuse)
    assert main([str(notes), "--out", str(out)], model=StubModel(sample_payload)) == 1
    captured = capsys.readouterr()
    assert "could not write" in captured.err and "read-only file system" in captured.err
    assert captured.out.startswith("# Epic:")
