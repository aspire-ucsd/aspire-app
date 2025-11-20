from typing import Optional, List, Annotated, Literal
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, ARRAY, Integer, VARCHAR
from sqlalchemy import ForeignKey


class TriggerEventBase(SQLModel):
    datetime_stamp: datetime
    student_id: int = Field(foreign_key="client.id", ondelete="CASCADE")
    concept: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE"),
        )
    )
    value: float
    weight: float

class TriggerEvent(TriggerEventBase, table=True):
    __tablename__ = ("trigger_event")
    event_id: Optional[int] = Field(default=None, primary_key=True)

class TriggerEventCreate(TriggerEventBase):
    pass

class TriggerEventRead(TriggerEventBase):
    pass

class TriggerEventProcess(SQLModel):
    event_ids: list[float]
    concept: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE")
        )
    )
    student_id: int = Field(foreign_key="client.id")
    numerator: float
    denominator: float