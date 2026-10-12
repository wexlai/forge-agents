"""Builds agent folders on disk for tests."""

from pathlib import Path

import yaml

HEADINGS = ("What it does", "Quick start", "Configuration", "How it works", "Examples", "Limitations")
README = "# Forge Spec\n\n" + "".join(f"## {h}\n\nText.\n\n" for h in HEADINGS)
ENV = "MODEL_PROVIDER=openai\nMODEL_ID=gpt-5\nOPENAI_API_KEY=\n# MODEL_PROVIDER=anthropic\n"

VALID_MANIFEST = {
    "id": "spec",
    "name": "Forge Spec",
    "framework": "strands",
    "language": "python",
    "status": "beta",
    "description": "Turns notes into stories",
    "catalog": "https://wexlai.com/forge/forge-spec",
    "providers": ["openai", "anthropic"],
    "commands": {"setup": "uv sync", "test": "uv run pytest", "example": "uv run forge-spec examples/a.input.txt"},
    "runtime": {"python": "3.12"},
    "maintainers": ["@wexlai/forge"],
}


def write_agent(
    root: Path,
    folder: str = "forge-spec-strands-python",
    manifest: dict | None = None,
    drop: tuple[str, ...] = (),
    readme: str | None = README,
    env: str | None = ENV,
    examples: tuple[str, ...] = ("demo.input.txt", "demo.output.md"),
) -> Path:
    d = root / folder
    (d / "examples").mkdir(parents=True)
    m = {**VALID_MANIFEST, **(manifest or {})}
    for key in drop:
        m.pop(key)
    (d / "agent.yaml").write_text(yaml.safe_dump(m, sort_keys=False), encoding="utf-8")
    if readme is not None:
        (d / "README.md").write_text(readme, encoding="utf-8")
    if env is not None:
        (d / ".env.example").write_text(env, encoding="utf-8")
    for name in examples:
        (d / "examples" / name).write_text("x", encoding="utf-8")
    return d
