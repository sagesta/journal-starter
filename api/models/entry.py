from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import uuid4
from datetime import datetime
import re

class Entry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the entry (UUID).")

    work: str = Field(..., min_length=3, max_length=256, description="What did you work on today?")

    struggle: str = Field(..., min_length=3, max_length=256, description="What’s one thing you struggled with today?")

    intention: str = Field(..., min_length=3, max_length=256, description="What will you study/work on tomorrow?")

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp when the entry was created.")

    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp when the entry was last updated.")
    
    schema_version: int = Field(default=1, description="Schema version for the entry.")

    @validator('work', 'struggle', 'intention')
    def sanitize_text(cls, v):
        v = v.strip()
        v = re.sub(r'<[^>]+>', '', v)

        if not v:
            raise ValueError('Field cannot be empty or only whitespace')
        return v

    class Config:
        pass
