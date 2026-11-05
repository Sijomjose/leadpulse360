import re
import unicodedata
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "aol.com",
    "mail.com",
    "proton.me",
    "protonmail.com",
}


def clean_text(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    # Normalize unicode characters and strip surrounding whitespace
    normalized = unicodedata.normalize("NFKC", str(text)).strip()
    return re.sub(r"\s+", " ", normalized)


class InboundLead(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=60)
    last_name: str = Field(..., min_length=1, max_length=60)
    work_email: EmailStr
    company_name: str = Field(..., min_length=1, max_length=120)
    company_size: int = Field(..., ge=1, le=1_000_000)
    annual_budget: float = Field(..., ge=0.0)
    industry: str = Field(..., min_length=2, max_length=80)
    urgency_months: int = Field(..., ge=1, le=36)
    use_case_notes: Optional[str] = Field(default="", max_length=2000)

    @field_validator("first_name", "last_name", "company_name", "industry", mode="before")
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        cleaned = clean_text(v)
        if not cleaned:
            raise ValueError("Field cannot be blank or pure whitespace.")
        return cleaned

    @field_validator("use_case_notes", mode="before")
    @classmethod
    def sanitize_optional_notes(cls, v: Optional[str]) -> str:
        return clean_text(v) or ""

    @property
    def email_domain(self) -> str:
        return self.work_email.split("@")[-1].lower()

    @property
    def is_corporate_domain(self) -> bool:
        return self.email_domain not in FREE_EMAIL_DOMAINS
