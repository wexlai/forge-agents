import pytest

import forge_repo
from agent_fixtures import HEADINGS, README, write_agent

NAME = "forge-spec-strands-python"


def test_valid_folder_has_no_errors(tmp_path):
    write_agent(tmp_path)
    assert forge_repo.validate(tmp_path) == []


def test_language_part_of_folder_name_is_optional(tmp_path):
    write_agent(tmp_path, folder="forge-spec-strands")
    assert forge_repo.validate(tmp_path) == []


def test_folder_name_must_match_manifest(tmp_path):
    write_agent(tmp_path, folder="forge-spec-crewai-python")
    assert forge_repo.validate(tmp_path) == [
        "forge-spec-crewai-python: folder name must be one of: forge-spec-strands, forge-spec-strands-python"
    ]


def test_non_agent_folders_are_ignored(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "templates").mkdir()
    write_agent(tmp_path)
    assert forge_repo.validate(tmp_path) == []


def test_missing_key(tmp_path):
    write_agent(tmp_path, drop=("maintainers",))
    assert forge_repo.validate(tmp_path) == [f"{NAME}: agent.yaml: missing key 'maintainers'"]


@pytest.mark.parametrize(
    "override, message",
    [
        ({"framework": "crew-ai"}, "agent.yaml: unknown framework 'crew-ai' (add it to FRAMEWORKS in tools/forge_repo.py)"),
        ({"language": "rust"}, "agent.yaml: unknown language 'rust' (add it to LANGUAGES in tools/forge_repo.py)"),
        ({"status": "alpha"}, "agent.yaml: status must be one of: experimental, beta, live, deprecated"),
        ({"providers": []}, "agent.yaml: providers must be a non-empty list"),
        ({"providers": ["openai", "groq"]}, "agent.yaml: unknown provider 'groq'"),
        ({"runtime": {"python": 3.12}}, 'agent.yaml: runtime version must be a quoted string, e.g. "3.12"'),
        ({"runtime": {"python": "3.12", "node": "22"}}, "agent.yaml: runtime must have exactly one key"),
        ({"runtime": {"ruby": "3.3"}}, "agent.yaml: unknown runtime 'ruby'"),
        ({"commands": {"setup": "uv sync", "test": "uv run pytest"}}, "agent.yaml: commands.example must be a non-empty string"),
        ({"commands": "uv sync"}, "agent.yaml: commands must be a mapping"),
        ({"id": "Spec"}, "agent.yaml: id must be a lowercase slug like 'spec'"),
        ({"name": ""}, "agent.yaml: name must be a non-empty string"),
        ({"description": "x" * 121}, "agent.yaml: description must be at most 120 characters"),
        ({"catalog": "wexlai.com/forge"}, "agent.yaml: catalog must be an https:// URL"),
        ({"maintainers": []}, "agent.yaml: maintainers must be a non-empty list of GitHub users or teams"),
    ],
)
def test_manifest_rule(tmp_path, override, message):
    write_agent(tmp_path, manifest=override)
    assert f"{NAME}: {message}" in forge_repo.validate(tmp_path)


def test_catalog_is_optional(tmp_path):
    write_agent(tmp_path, drop=("catalog",))
    assert forge_repo.validate(tmp_path) == []


def test_missing_manifest(tmp_path):
    d = write_agent(tmp_path)
    (d / "agent.yaml").unlink()
    assert forge_repo.validate(tmp_path) == [f"{NAME}: agent.yaml is missing"]


def test_invalid_yaml_is_reported_not_raised(tmp_path):
    d = write_agent(tmp_path)
    (d / "agent.yaml").write_text("id: [unclosed\n", encoding="utf-8")
    errors = forge_repo.validate(tmp_path)
    assert len(errors) == 1
    assert errors[0].startswith(f"{NAME}: agent.yaml is not valid YAML")


def test_yaml_list_root_is_reported(tmp_path):
    d = write_agent(tmp_path)
    (d / "agent.yaml").write_text("- id\n- name\n", encoding="utf-8")
    assert forge_repo.validate(tmp_path) == [f"{NAME}: agent.yaml must be a mapping"]


def test_readme_missing(tmp_path):
    write_agent(tmp_path, readme=None)
    assert forge_repo.validate(tmp_path) == [f"{NAME}: README.md is missing"]


def test_readme_headings_out_of_order(tmp_path):
    swapped = ("Quick start", "What it does") + HEADINGS[2:]
    write_agent(tmp_path, readme="# X\n\n" + "".join(f"## {h}\n\n" for h in swapped))
    assert forge_repo.validate(tmp_path) == [
        f"{NAME}: README.md: needs these ## headings in order: "
        "What it does, Quick start, Configuration, How it works, Examples, Limitations"
    ]


def test_readme_extra_headings_are_allowed(tmp_path):
    write_agent(tmp_path, readme=README.replace("## Limitations", "## Troubleshooting\n\nText.\n\n## Limitations"))
    assert forge_repo.validate(tmp_path) == []


def test_env_example_missing(tmp_path):
    write_agent(tmp_path, env=None)
    assert forge_repo.validate(tmp_path) == [f"{NAME}: .env.example is missing"]


def test_env_example_needs_model_id(tmp_path):
    write_agent(tmp_path, env="MODEL_PROVIDER=openai\n")
    assert forge_repo.validate(tmp_path) == [f"{NAME}: .env.example: MODEL_ID must be set"]


def test_env_example_provider_must_match_manifest(tmp_path):
    write_agent(tmp_path, env="MODEL_PROVIDER=anthropic\nMODEL_ID=claude-sonnet-5-5\n")
    assert forge_repo.validate(tmp_path) == [
        f"{NAME}: .env.example: MODEL_PROVIDER is 'anthropic' but providers[0] in agent.yaml is 'openai'"
    ]


def test_env_example_ignores_comments_and_quotes(tmp_path):
    write_agent(tmp_path, env='# MODEL_PROVIDER=anthropic\nMODEL_PROVIDER="openai"\nMODEL_ID=gpt-5\n')
    assert forge_repo.validate(tmp_path) == []


@pytest.mark.parametrize(
    "examples",
    [(), ("demo.input.txt",), ("a.input.txt", "b.output.md"), ("demo.txt", "demo.md")],
)
def test_examples_need_a_matching_pair(tmp_path, examples):
    write_agent(tmp_path, examples=examples)
    assert forge_repo.validate(tmp_path) == [
        f"{NAME}: examples/ needs at least one <name>.input.<ext> and <name>.output.<ext> pair"
    ]


def test_validate_named_folders_only(tmp_path):
    write_agent(tmp_path)
    write_agent(tmp_path, folder="forge-test-strands-python", manifest={"id": "test"}, readme=None)
    assert forge_repo.validate(tmp_path, ["forge-spec-strands-python/"]) == []


def test_validate_unknown_folder(tmp_path):
    assert forge_repo.validate(tmp_path, ["forge-nope"]) == ["forge-nope: no such agent folder"]


def test_cli_validate_exit_codes(tmp_path, capsys):
    write_agent(tmp_path)
    assert forge_repo.main(["--root", str(tmp_path), "validate"]) == 0
    assert "ok" in capsys.readouterr().out
    write_agent(tmp_path, folder="forge-bad-strands", manifest={"id": "bad"}, env=None)
    assert forge_repo.main(["--root", str(tmp_path), "validate"]) == 1
    assert "forge-bad-strands: .env.example is missing" in capsys.readouterr().out
