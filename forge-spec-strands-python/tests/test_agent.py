from conftest import StubModel

from forge_spec.agent import generate_spec
from forge_spec.inputs import SourceDocument
from forge_spec.prompt import SYSTEM_PROMPT, build_user_prompt

SOURCE = SourceDocument(name="notes.md", text="# Notes\nPM: ship the retry button\n")


def test_build_user_prompt_numbers_lines():
    prompt = build_user_prompt(SOURCE)
    assert "Source file: notes.md" in prompt
    assert "   1| # Notes\n   2| PM: ship the retry button\n" in prompt
    assert prompt.rstrip().endswith("</source>")


def test_generate_spec_returns_the_typed_result(sample_payload, sample_result):
    stub = StubModel(sample_payload)
    assert generate_spec(SOURCE, stub) == sample_result


def test_generate_spec_sends_system_prompt_source_and_output_tool(sample_payload):
    stub = StubModel(sample_payload)
    generate_spec(SOURCE, stub)
    call = stub.calls[0]
    assert call["system_prompt"] == SYSTEM_PROMPT
    assert "SpecResult" in [spec["name"] for spec in call["tool_specs"]]
    assert call["messages"][0]["content"][0]["text"] == build_user_prompt(SOURCE)


def test_system_prompt_states_the_core_rules():
    for rule in ("Use only what the source says", "line N", "Assumptions", "Open questions", "by role"):
        assert rule in SYSTEM_PROMPT
