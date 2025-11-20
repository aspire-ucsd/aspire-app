# app/domain/models/prompt.py
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import uuid4, UUID

class PromptBase(SQLModel):
    id: str = Field(primary_key=True)
    editable_part: str
    fixed_part: str

class Prompt(PromptBase, table=True):
    pass

class PromptCreate(PromptBase):
    pass

class PromptRead(PromptBase):
    pass

class PromptUpdate(SQLModel):
    editable_part: Optional[str] = None
    fixed_part: Optional[str] = None
