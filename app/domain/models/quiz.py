from typing import Optional, List, Annotated, Literal, Dict
import enum
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, ARRAY, Integer, Enum
from sqlalchemy.dialects.postgresql import JSON


class QuizTypes(str, enum.Enum):
    prerequisite = 'prereq'
    preview = 'preview'
    review = 'review'


class QuizBase(SQLModel):
    id: Optional[int] = Field(
        sa_column=Column("id", Integer, unique=True, primary_key=True
        )
    )
    collection_id: int = Field(foreign_key="concept_collection.id")
    course_id: int = Field(foreign_key="course.id")
    sme_input: Dict = Field(default={}, sa_column=Column(JSON))
    sme_importance: float = Field(default=0.0, le=1.0, ge=0.0)
    n_questions: int = Field(default=5, ge=1)
    type: QuizTypes = Field(sa_column=Column(Enum(QuizTypes)))
    due_date: datetime


class Quiz(QuizBase, table=True):
    pass


class QuizResultBase(SQLModel):
    quiz_id: int = Field(foreign_key="quiz.id", primary_key=True)
    student_id: int = Field(foreign_key="client.id", primary_key=True)
    correct: Optional[int] = Field(...)
    total: Optional[int] = Field(...)
    total_time_taken_secs: Optional[int]

class QuizResult(QuizResultBase, table=True):
    __tablename__ = "quiz_result"

