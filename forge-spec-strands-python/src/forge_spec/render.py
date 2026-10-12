"""Renders a SpecResult as Markdown (the catalog format) or as a Jira import CSV."""

import csv
import io

from forge_spec.models import Criterion, OpenQuestion, SpecResult, Story


def _refs(sources: list[str]) -> str:
    return f" [{', '.join(sources)}]" if sources else ""


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "?", "!")) else f"{text}."


def _clause(text: str) -> str:
    return text.strip().rstrip(",.")


def _criterion(c: Criterion) -> str:
    if c.given or c.when:
        parts = [f"Given {_clause(c.given)}" if c.given else "", f"when {_clause(c.when)}" if c.when else ""]
        parts = [p for p in parts if p] + [f"then {c.then.strip()}"]
    else:
        parts = [c.then.strip()]
    body = ",\n  ".join(parts[:-1] + [_sentence(parts[-1])])
    return f"- {body}{_refs(c.sources)}"


def _user_story(story: Story) -> list[str]:
    return [
        f"As {_clause(story.as_a)},",
        f"I want {_clause(story.i_want)},",
        _sentence(f"so that {story.so_that.strip()}"),
    ]


def _open_question(q: OpenQuestion) -> str:
    text = f"**{q.question.strip()}**"
    if q.detail.strip():
        text += f" {_sentence(q.detail)}"
    if q.owner:
        text += f" Owner: {_sentence(q.owner)}"
    return text + _refs(q.sources)


def to_markdown(result: SpecResult) -> str:
    single = len(result.epics) == 1
    source_line = (
        f"**Source:** {_sentence(result.source_label)} "
        f"References in [brackets] are {_sentence(result.reference_style)}"
    )
    if single:
        epic = result.epics[0]
        lines = [f"# Epic: {epic.title}", "", f"**Goal:** {_sentence(epic.goal)}", source_line, ""]
    else:
        lines = [f"# Spec: {result.source_label}", "", source_line, ""]

    if result.open_questions:
        lines += ["## Open questions (resolve before sizing)", ""]
        lines += [f"{i}. {_open_question(q)}" for i, q in enumerate(result.open_questions, start=1)]
        lines.append("")

    if single:
        lines += ["## Stories", ""]
    number = 0
    for epic_number, epic in enumerate(result.epics, start=1):
        if not single:
            lines += [f"## Epic {epic_number}: {epic.title}", "", f"**Goal:** {_sentence(epic.goal)}", ""]
        for story in epic.stories:
            number += 1
            lines += [f"### {number}. {story.title}", "", *_user_story(story), "", "**Acceptance criteria**", ""]
            lines += [_criterion(c) for c in story.criteria]
            lines.append("")

    if result.assumptions:
        lines += ["## Assumptions (not stated in the source; confirm or correct)", ""]
        lines += [f"- {_sentence(n.text)}{_refs(n.sources)}" for n in result.assumptions]
        lines.append("")
    if result.out_of_scope:
        lines += ["## Out of scope (raised and parked)", ""]
        lines += [f"- {_sentence(n.text)}{_refs(n.sources)}" for n in result.out_of_scope]
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def to_jira_csv(result: SpecResult) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["Issue Id", "Parent", "Issue Type", "Summary", "Description"])
    number = 0
    for epic_number, epic in enumerate(result.epics, start=1):
        epic_id = f"E{epic_number}"
        writer.writerow([epic_id, "", "Epic", epic.title, _sentence(epic.goal)])
        for story in epic.stories:
            number += 1
            description = "\n".join(
                [*_user_story(story), "", "Acceptance criteria", *(_criterion(c) for c in story.criteria)]
            )
            writer.writerow([f"S{number}", epic_id, "Story", story.title, description])
    return buffer.getvalue()
