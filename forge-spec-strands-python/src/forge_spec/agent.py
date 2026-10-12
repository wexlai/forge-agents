"""Runs the Strands agent that produces a SpecResult."""

from strands import Agent
from strands.models.model import Model

from forge_spec.inputs import SourceDocument
from forge_spec.models import SpecResult
from forge_spec.prompt import SYSTEM_PROMPT, build_user_prompt


class SpecGenerationError(Exception):
    """The model did not produce a usable spec."""


def generate_spec(source: SourceDocument, model: Model) -> SpecResult:
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, callback_handler=None)
    result = agent(build_user_prompt(source), structured_output_model=SpecResult)
    spec = result.structured_output
    if not isinstance(spec, SpecResult):
        raise SpecGenerationError("the model did not return a structured spec")
    return spec
