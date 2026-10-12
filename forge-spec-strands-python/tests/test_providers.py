import pytest
from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel
from strands.models.openai import OpenAIModel

from forge_spec.providers import ConfigError, build_model


def test_default_is_openai_gpt5():
    model = build_model({"OPENAI_API_KEY": "sk-test"})
    assert isinstance(model, OpenAIModel)
    assert model.get_config()["model_id"] == "gpt-5"


def test_model_id_override():
    model = build_model({"MODEL_PROVIDER": "openai", "MODEL_ID": "gpt-5-mini", "OPENAI_API_KEY": "sk-test"})
    assert model.get_config()["model_id"] == "gpt-5-mini"


def test_provider_name_is_case_insensitive():
    assert isinstance(build_model({"MODEL_PROVIDER": " OpenAI ", "OPENAI_API_KEY": "sk-test"}), OpenAIModel)


def test_anthropic():
    model = build_model({"MODEL_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "sk-ant-test"})
    assert isinstance(model, AnthropicModel)
    assert model.get_config()["model_id"] == "claude-sonnet-5-5"
    assert model.get_config()["max_tokens"] == 16000


def test_anthropic_max_tokens():
    model = build_model({"MODEL_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k", "MAX_TOKENS": "8000"})
    assert model.get_config()["max_tokens"] == 8000


def test_max_tokens_must_be_a_positive_integer():
    with pytest.raises(ConfigError, match="MAX_TOKENS must be a positive integer"):
        build_model({"MODEL_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k", "MAX_TOKENS": "lots"})


def test_bedrock_uses_sdk_default_model_when_unset(monkeypatch):
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    model = build_model({"MODEL_PROVIDER": "bedrock", "AWS_REGION": "us-east-1"})
    assert isinstance(model, BedrockModel)
    assert model.get_config()["model_id"]


def test_bedrock_model_id(monkeypatch):
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    model = build_model({"MODEL_PROVIDER": "bedrock", "AWS_REGION": "us-east-1", "MODEL_ID": "my-model"})
    assert model.get_config()["model_id"] == "my-model"


@pytest.mark.parametrize("env", [{}, {"OPENAI_API_KEY": ""}, {"OPENAI_API_KEY": "   "}])
def test_missing_openai_key(env):
    with pytest.raises(ConfigError, match="MODEL_PROVIDER=openai needs OPENAI_API_KEY"):
        build_model(env)


def test_missing_anthropic_key():
    with pytest.raises(ConfigError, match="MODEL_PROVIDER=anthropic needs ANTHROPIC_API_KEY"):
        build_model({"MODEL_PROVIDER": "anthropic", "OPENAI_API_KEY": "sk-test"})


def test_unknown_provider():
    with pytest.raises(ConfigError, match=r"Unknown MODEL_PROVIDER 'groq'\. Use one of: anthropic, bedrock, openai\."):
        build_model({"MODEL_PROVIDER": "groq"})
