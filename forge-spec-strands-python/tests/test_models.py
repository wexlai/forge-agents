import pytest
from pydantic import ValidationError

from forge_spec.models import SpecResult


def test_sample_validates(sample_result):
    criterion = sample_result.epics[0].stories[0].criteria[1]
    assert criterion.given is None and criterion.when is None
    assert sample_result.assumptions[0].sources == []


def test_every_criterion_needs_a_source(sample_payload):
    sample_payload["epics"][0]["stories"][0]["criteria"][0]["sources"] = []
    with pytest.raises(ValidationError):
        SpecResult.model_validate(sample_payload)


def test_a_story_needs_criteria(sample_payload):
    sample_payload["epics"][0]["stories"][0]["criteria"] = []
    with pytest.raises(ValidationError):
        SpecResult.model_validate(sample_payload)


def test_a_result_needs_an_epic(sample_payload):
    sample_payload["epics"] = []
    with pytest.raises(ValidationError):
        SpecResult.model_validate(sample_payload)
