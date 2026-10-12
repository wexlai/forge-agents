"""Loads a transcript or notes file into plain text."""

import re
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_SUFFIXES = (".txt", ".md", ".vtt")

_VOICE = re.compile(r"<v(?:\.[\w.-]+)*\s+([^>]+)>")
_TAG = re.compile(r"<[^>]+>")


class InputError(Exception):
    """The input file cannot be used."""


@dataclass(frozen=True)
class SourceDocument:
    name: str
    text: str


def _hhmmss(timestamp: str) -> str:
    parts = timestamp.replace(",", ".").split(".")[0].split(":")
    if len(parts) == 2:
        parts.insert(0, "00")
    return ":".join(p.zfill(2) for p in parts)


def vtt_to_text(raw: str) -> str:
    """WebVTT cues become '[hh:mm:ss] Speaker: text' lines."""
    lines_out = []
    for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n").strip()):
        lines = block.split("\n")
        if lines[0].startswith(("WEBVTT", "NOTE", "STYLE", "REGION")):
            continue
        timing = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing is None:
            continue
        stamp = _hhmmss(lines[timing].split("-->")[0].strip())
        text = " ".join(line.strip() for line in lines[timing + 1 :] if line.strip())
        text = _TAG.sub("", _VOICE.sub(r"\1: ", text)).strip()
        if text:
            lines_out.append(f"[{stamp}] {text}")
    return "".join(f"{line}\n" for line in lines_out)


def load_source(path: Path) -> SourceDocument:
    if not path.exists():
        raise InputError(f"{path}: file not found")
    if not path.is_file():
        raise InputError(f"{path}: not a file")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise InputError(
            f"{path}: unsupported file type '{suffix or 'none'}'. Supported: {', '.join(SUPPORTED_SUFFIXES)}"
        )
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"{path}: not UTF-8 text") from exc
    text = vtt_to_text(raw) if suffix == ".vtt" else raw.replace("\r\n", "\n")
    if not text.strip():
        raise InputError(f"{path}: file is empty")
    return SourceDocument(name=path.name, text=text)
