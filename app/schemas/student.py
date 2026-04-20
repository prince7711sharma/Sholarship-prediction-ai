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
        if not v:
            raise ValueError("Category cannot be empty")
        
        v = v.strip().upper()
        valid = ["GENERAL", "OBC", "SC", "ST", "EWS"]
        
        # Map some common variations
        mapping = {
            "OPEN": "GENERAL",
            "UNRESERVED": "GENERAL",
            "OTHER BACKWARD CLASS": "OBC",
            "SCHEDULED CASTE": "SC",
            "SCHEDULED TRIBE": "ST",
            "ECONOMICALLY WEAKER SECTION": "EWS"
        }
        
        if v in mapping:
            v = mapping[v]
            
        if v not in valid:
            # Try title case if upper didn't match (for General)
            v_title = v.capitalize()
            if v_title in ["General", "OBC", "SC", "ST", "EWS"]:
                return v_title
            
            # Final check against the backend expected format (Title Case)
            final_valid = ["General", "OBC", "SC", "ST", "EWS"]
            for opt in final_valid:
                if v == opt.upper():
                    return opt
                    
            raise ValueError(f"Category must be one of: {', '.join(final_valid)}")
        
        # Convert back to Title Case for internal consistency
        for opt in ["General", "OBC", "SC", "ST", "EWS"]:
            if v == opt.upper():
                return opt
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