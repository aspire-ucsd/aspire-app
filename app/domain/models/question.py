from datetime import date
import enum
from typing import Annotated, List, Literal, Optional

from sqlmodel import ARRAY, Column, Field, Integer, SQLModel, Enum, VARCHAR
from sqlalchemy import ForeignKey


class QuestionTypes(str, enum.Enum):
    multiple_choice = 'multiple choice'
    true_or_false = 'true/false'
    fill_in_the_blank = 'fill in the blank'
    fill_in_multiple_blanks = 'fill in multiple blanks'
    multiple_answers = 'multiple answers'
    multiple_dropdowns = 'multiple dropdowns'
    matching = 'matching'
    numerical_answer = 'numerical answer'
    formula_question = 'formula question'
    essay_question = 'essay question'
    file_upload_question = 'file upload question'
    text = 'text'


class AnswerBase(SQLModel):
    # Not required from LLM
    answer_text: str
    # 100 if correct, 0 if incorrect
    answer_weight: int
    answer_feedback: Optional[str]

class AnswerBaseExtended(AnswerBase):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: Optional[int] = Field(default=None, foreign_key="question.id", ondelete="CASCADE")

class Answer(AnswerBaseExtended, table=True):
    pass

class QuestionBase(SQLModel):
    # TODO: Add a foreign key relation from the concept name.
    id: Optional[int] = Field(default=None, primary_key=True)
    concept_name: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE")
        )
    )
    # Not required from LLM
    question_type: QuestionTypes = Field(sa_column=Column(Enum(QuestionTypes)))
    question_text: str
    # Not required from LLM
    points_possible: int

class Question(QuestionBase, table=True):
    pass

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    pass

class AnswerRead(AnswerBaseExtended):
    pass

class AnswerPreCreate(AnswerBase):
    pass

class AnswerCreate(AnswerBaseExtended):
    pass


class QuestionAnswerInput(SQLModel):
    question: QuestionCreate
    answers: List[AnswerPreCreate]


class QuestionAnswerSelection(SQLModel):
    question: Question
    answers: List[AnswerRead]
