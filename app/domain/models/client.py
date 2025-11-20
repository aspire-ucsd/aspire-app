from typing import Optional, List, Annotated, Literal, Dict, Union
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, ARRAY, Integer, JSON, String, VARCHAR

from sqlalchemy import ForeignKey
from sqlalchemy import event
from sqlalchemy.orm.attributes import flag_modified

import json

class ClientBase(SQLModel):
    # TODO: Create an Index on this.
    platform_id: Optional[str] = Field(...)


class Client(ClientBase, table=True):
    # Anonymized version of ID coming in from the platform
    id: Optional[int] = Field(default=None, primary_key=True)

class ClientCreate(ClientBase):
    pass


class ClientRead(Client):
    pass


class ClientToCourseBase(SQLModel):
    client_id: int = Field(foreign_key="client.id", primary_key=True, ondelete="CASCADE")
    course_id: int = Field(foreign_key="course.id", primary_key=True, ondelete="CASCADE")
    is_sme: bool

class ClientToCourse(ClientToCourseBase, table=True):
    __tablename__ = ("client_to_course")
    pass

class ClientToCourseRead(ClientToCourseBase):
    pass

class ClientToCourseCreate(ClientToCourseBase):
    pass


class StudentKnowledgeBase(SQLModel):
    student_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("client.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True
        )
    )
    concept_name: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True
        )
    )
    numerator: float
    denominator: float
    score: float = Field(default=0.5, le=1.0, ge=0.0)
    no_of_inputs: Optional[int] = Field(default=0)
    change_history: Optional[List[Dict[str, Union[str, float, int]]]] = Field(default=None, sa_column=Column("change_history", JSON(), nullable=True))


class StudentKnowledge(StudentKnowledgeBase, table=True):
    __tablename__ = ("student_knowledge")
    pass

class StudentKnowledgeRead(StudentKnowledgeBase):
    pass

class StudentKnowledgeCreate(StudentKnowledgeBase):
    pass


def update_change_history(mapper, connection, target):
    if target.change_history is None:
        target.change_history = []

    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "score": target.score,
        "no_of_inputs": target.no_of_inputs
        
    }
    flag_modified(target, 'change_history')
    target.change_history.append(new_entry)
    


event.listen(StudentKnowledge, 'before_insert', update_change_history)
event.listen(StudentKnowledge, 'before_update', update_change_history)