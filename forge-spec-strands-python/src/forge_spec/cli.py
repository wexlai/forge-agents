"""forge-spec: turn a transcript or notes into epics, stories and acceptance criteria."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from strands.models.model import Model

from forge_spec.agent import generate_spec
from forge_spec.inputs import InputError, load_source
from forge_spec.providers import ConfigError, build_model
from forge_spec.render import to_jira_csv, to_markdown


def main(argv: list[str] | None = None, *, model: Model | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="forge-spec",
        description="Turn a meeting transcript or notes into epics, user stories and acceptance criteria.",
    )
    parser.add_argument("input", type=Path, help="transcript or notes (.txt, .md, .vtt)")
    parser.add_argument("--format", choices=("markdown", "jira-csv"), default="markdown")
    parser.add_argument("--out", type=Path, help="write to this file instead of standard output")
    args = parser.parse_args(argv)

    try:
        source = load_source(args.input)
        if args.out:
            _check_out(args.out)
        if model is None:
            load_dotenv(Path.cwd() / ".env")
            model = build_model(os.environ)
    except (InputError, ConfigError) as exc:
        print(f"forge-spec: {exc}", file=sys.stderr)
        return 2

    try:
        result = generate_spec(source, model)
    except Exception as exc:  # network, auth, rate limit or invalid model output
        print(f"forge-spec: generation failed: {exc}", file=sys.stderr)
        return 1

    output = to_markdown(result) if args.format == "markdown" else to_jira_csv(result)
    if args.out:
        try:
            args.out.write_text(output, encoding="utf-8")
            return 0
        except OSError as exc:
            # The model call is already paid for: keep the result rather than lose it.
            print(f"forge-spec: could not write {args.out}: {exc}; printing the result instead", file=sys.stderr)
            sys.stdout.write(output)
            return 1
    sys.stdout.write(output)
    return 0


def _check_out(out: Path) -> None:
    """Fail before the model call if --out cannot be written."""
    if out.is_dir():
        raise InputError(f"--out {out}: is a directory")
    if not out.parent.is_dir():
        raise InputError(f"--out {out}: directory does not exist")
