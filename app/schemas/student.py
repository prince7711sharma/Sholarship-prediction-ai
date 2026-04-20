from pydantic import BaseModel, field_validator
from typing import Optional


class Student(BaseModel):
    marks: int
    category: str
    income: int
    state: str
    course: str
    gender: Optional[str] = None
    disability: Optional[bool] = False

    @field_validator("marks")
    @classmethod
    def validate_marks(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Marks must be between 0 and 100")
        return v

    @field_validator("income")
    @classmethod
    def validate_income(cls, v):
        if v < 0:
            raise ValueError("Income cannot be negative")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        valid = ["General", "OBC", "SC", "ST", "EWS"]
        if v not in valid:
            raise ValueError(f"Category must be one of: {', '.join(valid)}")
        return v

    @field_validator("state", "course")
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("This field cannot be empty")
        return v.strip()

    @property
    def percentage(self) -> float:
        return self.marks

    @property
    def income_bracket(self) -> str:
        if self.income <= 100000:
            return "Below 1 Lakh"
        elif self.income <= 250000:
            return "1-2.5 Lakh"
        elif self.income <= 500000:
            return "2.5-5 Lakh"
        elif self.income <= 800000:
            return "5-8 Lakh"
        else:
            return "Above 8 Lakh"