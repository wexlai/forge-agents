import re
import shutil
from pathlib import Path

import forge_repo

TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "agent"
VALUES = {
    "__ID__": "example",
    "__NAME__": "Forge Example",
    "__FRAMEWORK__": "strands",
    "__LANGUAGE__": "python",
    "__DESCRIPTION__": "An example agent",
}


def template_files():
    return [p for p in TEMPLATE.rglob("*") if p.is_file()]


def test_template_uses_only_known_placeholders():
    found = set()
    for path in template_files():
        found |= set(re.findall(r"__[A-Z]+__", path.read_text(encoding="utf-8")))
    assert found == set(VALUES)


def test_filled_template_passes_validate(tmp_path):
    target = tmp_path / "forge-example-strands-python"
    shutil.copytree(TEMPLATE, target)
    for path in target.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for key, value in VALUES.items():
                text = text.replace(key, value)
            path.write_text(text, encoding="utf-8")
    assert forge_repo.validate(tmp_path) == []
