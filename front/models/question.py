from typing import List

from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    """Represents a single quiz question."""

    country: str = Field(..., description="The name of the country")
    correct_answer: str = Field(..., description="The correct capital city")
    choices: List[str] = Field(..., description="List of capital city choices")
