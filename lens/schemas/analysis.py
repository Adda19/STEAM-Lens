from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

class DetectedObject(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=400)
    confidence: Literal["high", "medium", "low"]

class Connection(StrictModel):
    area: Literal["science", "technology", "engineering", "arts", "mathematics"]
    title: str = Field(min_length=1, max_length=100)
    explanation: str = Field(min_length=1, max_length=300)

class Mission(StrictModel):
    title: str = Field(min_length=1, max_length=100)
    challenge: str = Field(min_length=1, max_length=500)
    learning_goal: str = Field(min_length=1, max_length=400)
    difficulty: int = Field(ge=1, le=3)
    estimated_minutes: int = Field(ge=1, le=180)
    materials_required: list[str] = Field(max_length=10)
    first_question: str = Field(min_length=1, max_length=350)
    success_criteria: str = Field(min_length=1, max_length=500)

class Analysis(StrictModel):
    valid_capture: bool
    retry_message: str | None
    detected_object: DetectedObject | None
    steam_connections: list[Connection] = Field(max_length=5)
    mission: Mission | None

    @model_validator(mode="after")
    def coherent(self):
        if self.valid_capture:
            if not self.detected_object or not self.mission or not 2 <= len(self.steam_connections) <= 5 or self.retry_message is not None:
                raise ValueError("Incomplete valid analysis")
            areas = [c.area for c in self.steam_connections]
            if len(set(areas)) != len(areas):
                raise ValueError("Duplicate STEAM areas")
        elif self.mission is not None or self.detected_object is not None or self.steam_connections or not self.retry_message:
            raise ValueError("Invalid capture must only contain retry message")
        return self
