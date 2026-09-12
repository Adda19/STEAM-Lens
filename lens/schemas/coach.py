from typing import Literal
from pydantic import Field, model_validator
from .analysis import StrictModel

class CoachReply(StrictModel):
    feedback: str = Field(min_length=1, max_length=500)
    status: Literal["continue", "hint", "completed", "blocked"]
    hint_level: int = Field(ge=0, le=3)
    hint: str | None
    next_question: str | None
    celebration: str | None

    @model_validator(mode="after")
    def coherent(self):
        if self.status in {"continue", "hint"} and not self.next_question:
            raise ValueError("Continuing requires a question")
        if self.status in {"completed", "blocked"} and self.next_question is not None:
            raise ValueError("Terminal replies have no next question")
        if (self.hint_level == 0 and self.hint is not None) or (self.hint_level > 0 and not self.hint):
            raise ValueError("Hint level inconsistent")
        return self
