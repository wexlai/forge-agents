import copy
import json

import pytest
from strands.models.model import Model

from forge_spec.models import SpecResult

SAMPLE = {
    "source_label": "Refinement call, 21 min",
    "reference_style": "transcript timestamps",
    "epics": [
        {
            "title": "Retry the questions you missed",
            "goal": "Let a learner practise only the questions they got wrong",
            "stories": [
                {
                    "title": "Offer a retry on the result screen",
                    "as_a": "a learner who has just finished a Practice BET",
                    "i_want": "to retry only the questions I got wrong",
                    "so_that": "I can practise my weak spots",
                    "criteria": [
                        {
                            "given": "a learner got at least one question wrong",
                            "when": "the result screen loads",
                            "then": 'a button reads "Retry the N you missed"',
                            "sources": ["00:01:31"],
                        },
                        {"then": "The retry has no timer", "sources": ["00:08:31"]},
                    ],
                }
            ],
        }
    ],
    "open_questions": [
        {
            "question": "Which plans get this?",
            "detail": "All users, or the paid tier only?",
            "owner": "PM",
            "sources": ["00:09:10"],
        }
    ],
    "assumptions": [{"text": "An unanswered question counts as missed"}],
    "out_of_scope": [{"text": "Resuming an interrupted retry", "sources": ["00:10:39"]}],
}


@pytest.fixture
def sample_payload() -> dict:
    return copy.deepcopy(SAMPLE)


@pytest.fixture
def sample_result() -> SpecResult:
    return SpecResult.model_validate(SAMPLE)



class StubModel(Model):
    """Stands in for a real provider: answers by calling the first offered tool with a fixed payload.

    Strands delivers structured output through a tool named after the output model, so this drives the
    real agent loop without a network call.
    """

    def __init__(self, payload: dict | None = None, error: Exception | None = None):
        self.payload = payload
        self.error = error
        self.calls: list[dict] = []

    def update_config(self, **model_config):
        pass

    def get_config(self):
        return {}

    async def structured_output(self, output_model, prompt, system_prompt=None, **kwargs):
        yield {"output": output_model.model_validate(self.payload)}

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls.append({"messages": messages, "tool_specs": tool_specs, "system_prompt": system_prompt})
        if self.error is not None:
            raise self.error
        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockStart": {"start": {"toolUse": {"toolUseId": "t1", "name": tool_specs[0]["name"]}}}}
        yield {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(self.payload)}}}}
        yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": "tool_use"}}
