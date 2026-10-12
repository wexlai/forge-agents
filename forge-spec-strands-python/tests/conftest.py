import copy

import pytest

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
