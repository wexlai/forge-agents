import pytest

from forge_spec.inputs import InputError, load_source, vtt_to_text

VTT = """WEBVTT

NOTE recorded on a video call
second note line

1
00:00:15.000 --> 00:00:20.000
<v PM>Okay, one item today.</v>

2
00:01:31.500 --> 00:01:35.000
<v.loud Tech lead>Yes. Something like
"Retry the 3 you missed".

01:49.000 --> 01:52.000
Then don't show the button.
"""


def test_vtt_to_text_keeps_timestamps_and_speakers():
    assert vtt_to_text(VTT) == (
        "[00:00:15] PM: Okay, one item today.\n"
        '[00:01:31] Tech lead: Yes. Something like "Retry the 3 you missed".\n'
        "[00:01:49] Then don't show the button.\n"
    )


def test_load_txt(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("PM: ship it\n", encoding="utf-8")
    source = load_source(path)
    assert source.name == "notes.txt"
    assert source.text == "PM: ship it\n"


def test_load_md_with_crlf_and_bom(tmp_path):
    path = tmp_path / "notes.md"
    path.write_bytes("\ufeff# Notes\r\nline two\r\n".encode("utf-8"))
    assert load_source(path).text == "# Notes\nline two\n"


def test_load_vtt(tmp_path):
    path = tmp_path / "call.vtt"
    path.write_text(VTT, encoding="utf-8")
    assert load_source(path).text.startswith("[00:00:15] PM: Okay")


def test_suffix_is_case_insensitive(tmp_path):
    path = tmp_path / "NOTES.TXT"
    path.write_text("x\n", encoding="utf-8")
    assert load_source(path).text == "x\n"


@pytest.mark.parametrize(
    "name, content, message",
    [
        ("notes.docx", b"PK", "unsupported file type '.docx'. Supported: .txt, .md, .vtt"),
        ("notes", b"x", "unsupported file type 'none'. Supported: .txt, .md, .vtt"),
        ("empty.txt", b"", "file is empty"),
        ("blank.md", b"  \n\n\t\n", "file is empty"),
        ("latin1.txt", "caf\xe9".encode("latin-1"), "not UTF-8 text"),
        ("header-only.vtt", b"WEBVTT\n\n", "file is empty"),
    ],
)
def test_bad_inputs(tmp_path, name, content, message):
    path = tmp_path / name
    path.write_bytes(content)
    with pytest.raises(InputError, match=message.replace(".", r"\.")):
        load_source(path)


def test_missing_file(tmp_path):
    with pytest.raises(InputError, match="file not found"):
        load_source(tmp_path / "nope.txt")


def test_directory(tmp_path):
    (tmp_path / "dir.txt").mkdir()
    with pytest.raises(InputError, match="not a file"):
        load_source(tmp_path / "dir.txt")
