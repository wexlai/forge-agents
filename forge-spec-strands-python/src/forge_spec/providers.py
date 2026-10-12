"""Builds the Strands model named by MODEL_PROVIDER and MODEL_ID."""

from collections.abc import Mapping

from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel
from strands.models.model import Model
from strands.models.openai import OpenAIModel

PROVIDERS = ("anthropic", "bedrock", "openai")
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL_IDS = {"openai": "gpt-5", "anthropic": "claude-sonnet-5-5"}
API_KEY_VARS = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
DEFAULT_MAX_TOKENS = 16000


class ConfigError(Exception):
    """The environment does not describe a usable model."""


def _get(env: Mapping[str, str], key: str) -> str:
    return (env.get(key) or "").strip()


def _max_tokens(env: Mapping[str, str]) -> int:
    raw = _get(env, "MAX_TOKENS")
    if not raw:
        return DEFAULT_MAX_TOKENS
    if not raw.isdigit() or int(raw) <= 0:
        raise ConfigError(f"MAX_TOKENS must be a positive integer, got '{raw}'")
    return int(raw)


def build_model(env: Mapping[str, str]) -> Model:
    provider = (_get(env, "MODEL_PROVIDER") or DEFAULT_PROVIDER).lower()
    if provider not in PROVIDERS:
        raise ConfigError(f"Unknown MODEL_PROVIDER '{provider}'. Use one of: {', '.join(PROVIDERS)}.")
    model_id = _get(env, "MODEL_ID") or DEFAULT_MODEL_IDS.get(provider)

    api_key = ""
    if provider in API_KEY_VARS:
        api_key = _get(env, API_KEY_VARS[provider])
        if not api_key:
            raise ConfigError(
                f"MODEL_PROVIDER={provider} needs {API_KEY_VARS[provider]}. "
                "Set it in .env (copy .env.example) or in your shell."
            )

    if provider == "openai":
        return OpenAIModel(client_args={"api_key": api_key}, model_id=model_id)
    if provider == "anthropic":
        return AnthropicModel(client_args={"api_key": api_key}, model_id=model_id, max_tokens=_max_tokens(env))
    bedrock_args = {"model_id": model_id} if model_id else {}
    return BedrockModel(region_name=_get(env, "AWS_REGION") or None, **bedrock_args)
