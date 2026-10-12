import csv
import io

from forge_spec.models import SpecResult
from forge_spec.render import to_jira_csv, to_markdown

EXPECTED_MARKDOWN = """\
# Epic: Retry the questions you missed

**Goal:** Let a learner practise only the questions they got wrong.
**Source:** Refinement call, 21 min. References in [brackets] are transcript timestamps.

## Open questions (resolve before sizing)

1. **Which plans get this?** All users, or the paid tier only? Owner: PM. [00:09:10]

## Stories

### 1. Offer a retry on the result screen

As a learner who has just finished a Practice BET,
I want to retry only the questions I got wrong,
so that I can practise my weak spots.

**Acceptance criteria**

- Given a learner got at least one question wrong,
  when the result screen loads,
  then a button reads "Retry the N you missed". [00:01:31]
- The retry has no timer. [00:08:31]

## Assumptions (not stated in the source; confirm or correct)

- An unanswered question counts as missed.

## Out of scope (raised and parked)

- Resuming an interrupted retry. [00:10:39]
"""


def test_markdown_matches_the_catalog_format(sample_result):
    assert to_markdown(sample_result) == EXPECTED_MARKDOWN


def test_markdown_omits_empty_sections(sample_payload):
    for key in ("open_questions", "assumptions", "out_of_scope"):
        sample_payload[key] = []
    out = to_markdown(SpecResult.model_validate(sample_payload))
    assert "Open questions" not in out and "Assumptions" not in out and "Out of scope" not in out
    assert out.endswith("- The retry has no timer. [00:08:31]\n")


def test_markdown_criterion_without_when(sample_payload):
    sample_payload["epics"][0]["stories"][0]["criteria"] = [
        {"given": "exactly one question is wrong", "then": 'the button reads "Retry the one you missed"', "sources": ["00:12:38"]}
    ]
    out = to_markdown(SpecResult.model_validate(sample_payload))
    assert '- Given exactly one question is wrong,\n  then the button reads "Retry the one you missed". [00:12:38]\n' in out


def test_markdown_with_several_epics_numbers_stories_across_epics(sample_payload):
    second = {**sample_payload["epics"][0], "title": "Report retries"}
    sample_payload["epics"].append(second)
    out = to_markdown(SpecResult.model_validate(sample_payload))
    assert out.startswith("# Spec: Refinement call, 21 min\n\n**Source:** Refinement call, 21 min.")
    assert "## Epic 1: Retry the questions you missed" in out
    assert "## Epic 2: Report retries" in out
    assert "### 1. Offer a retry on the result screen" in out
    assert "### 2. Offer a retry on the result screen" in out
    assert "## Stories" not in out


def test_jira_csv_rows(sample_result):
    rows = list(csv.reader(io.StringIO(to_jira_csv(sample_result))))
    assert rows[0] == ["Issue Id", "Parent", "Issue Type", "Summary", "Description"]
    assert rows[1] == ["E1", "", "Epic", "Retry the questions you missed", "Let a learner practise only the questions they got wrong."]
    assert rows[2][:4] == ["S1", "E1", "Story", "Offer a retry on the result screen"]
    assert rows[2][4] == (
        "As a learner who has just finished a Practice BET,\n"
        "I want to retry only the questions I got wrong,\n"
        "so that I can practise my weak spots.\n\n"
        "Acceptance criteria\n"
        "- Given a learner got at least one question wrong,\n"
        "  when the result screen loads,\n"
        '  then a button reads "Retry the N you missed". [00:01:31]\n'
        "- The retry has no timer. [00:08:31]"
    )
    assert len(rows) == 3


def test_jira_csv_survives_awkward_text(sample_payload):
    awkward = 'Say "hi", then | go\nnow'
    sample_payload["epics"][0]["stories"][0]["title"] = awkward
    rows = list(csv.reader(io.StringIO(to_jira_csv(SpecResult.model_validate(sample_payload)))))
    assert rows[2][3] == awkward
