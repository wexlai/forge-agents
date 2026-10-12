"""The typed result Forge Spec asks the model for."""

from pydantic import BaseModel, Field


class Criterion(BaseModel):
    """One testable acceptance criterion."""

    given: str | None = Field(
        default=None, description="Precondition, without the word 'Given' or trailing punctuation. Empty for a plain rule."
    )
    when: str | None = Field(
        default=None, description="Trigger, without the word 'when' or trailing punctuation. Empty if there is none."
    )
    then: str = Field(
        description="Expected outcome without the word 'then'. For a plain rule (no given/when), the whole rule as a sentence."
    )
    sources: list[str] = Field(
        min_length=1,
        description="Where this came from: timestamps as 'hh:mm:ss', or 'line N' when the source has no timestamps.",
    )


class Story(BaseModel):
    """A user story with its acceptance criteria."""

    title: str = Field(description="Short imperative title, e.g. 'Offer a retry on the result screen'.")
    as_a: str = Field(description="The role, phrased to follow 'As', e.g. 'a learner who has just finished a Practice BET'.")
    i_want: str = Field(description="Phrased to follow 'I want', e.g. 'to retry only the questions I got wrong'.")
    so_that: str = Field(description="Phrased to follow 'so that'.")
    criteria: list[Criterion] = Field(min_length=1)


class Epic(BaseModel):
    """A goal that groups related stories."""

    title: str
    goal: str = Field(description="One sentence: what the epic achieves for whom.")
    stories: list[Story] = Field(min_length=1)


class OpenQuestion(BaseModel):
    """Something the source leaves undecided, or never discusses but a team would need."""

    question: str = Field(description="The question itself, e.g. 'Which plans get this?'.")
    detail: str = Field(default="", description="Context or what was said, in one or two sentences.")
    owner: str | None = Field(default=None, description="Who should answer it, only if the source names them (by role).")
    sources: list[str] = Field(default_factory=list)


class Note(BaseModel):
    """An assumption or an out-of-scope item."""

    text: str
    sources: list[str] = Field(default_factory=list)


class SpecResult(BaseModel):
    """Epics, user stories and acceptance criteria drawn from one source document."""

    source_label: str = Field(description="Short name for the source, e.g. 'Refinement call, 21 min'.")
    reference_style: str = Field(description="What the references mean, e.g. 'transcript timestamps' or 'line numbers in the notes'.")
    epics: list[Epic] = Field(min_length=1)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    assumptions: list[Note] = Field(
        default_factory=list, description="Things assumed to write the stories that the source does not state."
    )
    out_of_scope: list[Note] = Field(default_factory=list, description="Items the source raised and explicitly parked.")
