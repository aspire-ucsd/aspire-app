""" This files stores all the input parameters used in the QAS API calls."""
from typing import Literal, Dict, Union
from datetime import datetime

from pydantic import BaseModel, Field
from dataclasses import dataclass

from fastapi import Depends


class PersonalizedQuizProtocol(BaseModel):
    """ This class stores the input utilized to generate Personalized Quiz. """
    module_id: int = Field(...)
    canvas_access_token: str = Field(...)
    canvas_course_id: int = Field(...)
    sme_input: Union[Dict, None] = Field(default=None)
    sme_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    n_questions: int = Field(default=5, ge=1)
    quiz_type: Literal['prereq', 'preview', 'review']
    due_date: datetime = Field(...)


class PersonalizedQuestionProtocol(BaseModel):
    module_id: int = Field(...)
    sme_input: Union[Dict, None] = Field(default=None)
    sme_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    quiz_type: Literal['prereq', 'preview', 'review']

