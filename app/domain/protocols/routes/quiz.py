""" This files stores all the input parameters used in the Quiz API calls."""
from typing import Literal, Dict, Union, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from dataclasses import dataclass

from fastapi import Depends


class QuizParametersProtocol(BaseModel):
    """ This class stores the constraints placed on a Quiz."""
    module_id: int = Field(...)
    sme_input: Union[Dict, None] = Field(default=None)
    sme_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    n_questions: int = Field(default=5, ge=1)
    quiz_type: Literal['prereq', 'preview', 'review']
    due_date: datetime = Field(...)


class QuizResultsProtocol(BaseModel):
    """ This class stores the requirements associated with a QuizSubmission."""
    quiz_id: int = Field(...)
    correct: Optional[int] = Field(...)
    total: Optional[int] = Field(...)
    total_time_taken_secs: Optional[int] = Field(ge=0)
