# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Repo tooling for forge-agents.

  validate [FOLDER ...]                       check agent folders against the folder standard
  index [--check]                             rewrite (or check) the agent table in README.md
  matrix [--changed-from REF | --agent NAME]  print the CI matrix as JSON
  stale [--days N]                            list agent folders with no commit in N days

Run with: uv run tools/forge_repo.py <command>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

FRAMEWORKS = frozenset(
    {
        "strands", "crewai", "spring-ai", "embabel", "langgraph", "autogen",
        "pydantic-ai", "openai-agents", "claude-agent-sdk", "mastra", "semantic-kernel", "adk",
    }
)
LANGUAGES = frozenset({"python", "typescript", "java", "kotlin", "go", "csharp"})
STATUSES = ("experimental", "beta", "live", "deprecated")
PROVIDERS = frozenset({"anthropic", "bedrock", "openai", "azure-openai", "vertex", "gemini", "ollama"})
RUNTIMES = frozenset({"python", "node", "java", "go", "dotnet"})
COMMANDS = ("setup", "test", "example")
REQUIRED_KEYS = (
    "id", "name", "framework", "language", "status", "description",
    "providers", "commands", "runtime", "maintainers",
)
README_HEADINGS = ("What it does", "Quick start", "Configuration", "How it works", "Examples", "Limitations")
MAX_DESCRIPTION = 120
INDEX_START = "<!-- agents:start -->"
INDEX_END = "<!-- agents:end -->"
SHARED_PREFIXES = ("tools/", "templates/", ".github/")

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXAMPLE_FILE = re.compile(r"^(?P<name>.+)\.(?P<kind>input|output)\.[^.]+$")
HEADING = re.compile(r"^## (.+?)\s*$", re.MULTILINE)


def agent_folders(root: Path) -> list[Path]:
    return sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith("forge-"))


def load_manifest(folder: Path) -> dict:
    path = folder / "agent.yaml"
    if not path.is_file():
        raise ValueError("agent.yaml is missing")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"agent.yaml is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("agent.yaml must be a mapping")
    return data


def _non_empty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_manifest(m: dict) -> list[str]:
    errors = [f"agent.yaml: missing key '{k}'" for k in REQUIRED_KEYS if k not in m]
    if errors:
        return errors
    if not isinstance(m["id"], str) or not SLUG.match(m["id"]):
        errors.append("agent.yaml: id must be a lowercase slug like 'spec'")
    for key in ("name", "description"):
        if not _non_empty_str(m[key]):
            errors.append(f"agent.yaml: {key} must be a non-empty string")
    if isinstance(m["description"], str) and len(m["description"]) > MAX_DESCRIPTION:
        errors.append(f"agent.yaml: description must be at most {MAX_DESCRIPTION} characters")
    if m["framework"] not in FRAMEWORKS:
        errors.append(f"agent.yaml: unknown framework '{m['framework']}' (add it to FRAMEWORKS in tools/forge_repo.py)")
    if m["language"] not in LANGUAGES:
        errors.append(f"agent.yaml: unknown language '{m['language']}' (add it to LANGUAGES in tools/forge_repo.py)")
    if m["status"] not in STATUSES:
        errors.append(f"agent.yaml: status must be one of: {', '.join(STATUSES)}")
    providers = m["providers"]
    if not isinstance(providers, list) or not providers:
        errors.append("agent.yaml: providers must be a non-empty list")
    else:
        errors += [f"agent.yaml: unknown provider '{p}'" for p in providers if p not in PROVIDERS]
    commands = m["commands"]
    if not isinstance(commands, dict):
        errors.append("agent.yaml: commands must be a mapping")
    else:
        errors += [
            f"agent.yaml: commands.{c} must be a non-empty string" for c in COMMANDS if not _non_empty_str(commands.get(c))
        ]
    runtime = m["runtime"]
    if not isinstance(runtime, dict) or len(runtime) != 1:
        errors.append("agent.yaml: runtime must have exactly one key")
    else:
        kind, version = next(iter(runtime.items()))
        if kind not in RUNTIMES:
            errors.append(f"agent.yaml: unknown runtime '{kind}'")
        if not _non_empty_str(version):
            errors.append('agent.yaml: runtime version must be a quoted string, e.g. "3.12"')
    maintainers = m["maintainers"]
    if not isinstance(maintainers, list) or not maintainers or not all(_non_empty_str(x) for x in maintainers):
        errors.append("agent.yaml: maintainers must be a non-empty list of GitHub users or teams")
    if "catalog" in m and not (isinstance(m["catalog"], str) and m["catalog"].startswith("https://")):
        errors.append("agent.yaml: catalog must be an https:// URL")
    return errors


def read_env_example(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def has_example_pair(examples: Path) -> bool:
    if not examples.is_dir():
        return False
    kinds: dict[str, set[str]] = {}
    for path in examples.iterdir():
        match = EXAMPLE_FILE.match(path.name)
        if path.is_file() and match:
            kinds.setdefault(match["name"], set()).add(match["kind"])
    return any(k == {"input", "output"} for k in kinds.values())


def check_folder(folder: Path) -> list[str]:
    try:
        m = load_manifest(folder)
    except ValueError as exc:
        return [str(exc)]
    errors = check_manifest(m)
    if not errors:
        allowed = {f"forge-{m['id']}-{m['framework']}", f"forge-{m['id']}-{m['framework']}-{m['language']}"}
        if folder.name not in allowed:
            errors.append(f"folder name must be one of: {', '.join(sorted(allowed))}")

    readme = folder / "README.md"
    if not readme.is_file():
        errors.append("README.md is missing")
    else:
        found = iter(HEADING.findall(readme.read_text(encoding="utf-8")))
        if not all(h in found for h in README_HEADINGS):
            errors.append("README.md: needs these ## headings in order: " + ", ".join(README_HEADINGS))

    env_example = folder / ".env.example"
    if not env_example.is_file():
        errors.append(".env.example is missing")
    else:
        values = read_env_example(env_example)
        for key in ("MODEL_PROVIDER", "MODEL_ID"):
            if not values.get(key):
                errors.append(f".env.example: {key} must be set")
        providers = m.get("providers")
        provider = values.get("MODEL_PROVIDER")
        if provider and isinstance(providers, list) and providers and provider != providers[0]:
            errors.append(
                f".env.example: MODEL_PROVIDER is '{provider}' but providers[0] in agent.yaml is '{providers[0]}'"
            )

    if not has_example_pair(folder / "examples"):
        errors.append("examples/ needs at least one <name>.input.<ext> and <name>.output.<ext> pair")
    return errors


def validate(root: Path, names: list[str] | None = None) -> list[str]:
    folders = agent_folders(root)
    unknown: list[str] = []
    if names:
        by_name = {f.name: f for f in folders}
        wanted = [n.rstrip("/") for n in names]
        unknown = [f"{n}: no such agent folder" for n in wanted if n not in by_name]
        folders = [by_name[n] for n in wanted if n in by_name]
    return unknown + [f"{f.name}: {e}" for f in folders for e in check_folder(f)]


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_index(root: Path) -> str:
    rows = []
    for folder in agent_folders(root):
        m = load_manifest(folder)
        rows.append((m["id"], folder.name, m))
    rows.sort(key=lambda row: (row[0], row[1]))
    lines = [
        "| Agent | Framework | Language | Status | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    for _, name, m in rows:
        lines.append(
            f"| [{_cell(m['name'])}]({name}/) | {m['framework']} | {m['language']} | {m['status']} | {_cell(m['description'])} |"
        )
    if not rows:
        lines.append("| _No agents yet_ | | | | |")
    return "\n".join(lines)


def replace_index(readme_text: str, table: str) -> str:
    start = readme_text.find(INDEX_START)
    end = readme_text.find(INDEX_END)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"README.md must contain {INDEX_START} followed by {INDEX_END}")
    return readme_text[: start + len(INDEX_START)] + "\n" + table + "\n" + readme_text[end:]


def update_index(root: Path, check: bool = False) -> bool:
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    new = replace_index(text, render_index(root))
    if new == text:
        return True
    if not check:
        readme.write_text(new, encoding="utf-8")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="forge_repo", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    p_validate = sub.add_parser("validate", help="check agent folders")
    p_validate.add_argument("folders", nargs="*")
    p_index = sub.add_parser("index", help="rewrite the agent table in README.md")
    p_index.add_argument("--check", action="store_true", help="fail if the table is out of date; do not write")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.command == "validate":
        errors = validate(root, args.folders)
        for error in errors:
            print(error)
        if not errors:
            print("ok: all agent folders are valid")
        return 1 if errors else 0
    if args.command == "index":
        errors = validate(root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print("fix these before regenerating the index", file=sys.stderr)
            return 1
        try:
            current = update_index(root, check=args.check)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 1
        if args.check and not current:
            print("README.md agent table is out of date; run: uv run tools/forge_repo.py index", file=sys.stderr)
            return 1
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
