from typing import Optional, List, Literal
from datetime import date
from enum import Enum

from pydantic import BaseModel

from sqlmodel import Field, SQLModel, Column, ARRAY, Integer
from sqlalchemy.dialects.postgresql import JSONB


class CourseBase(SQLModel):
    name: str = Field(max_length=255)
    quarter: date
    instructor: str
    summary: Optional[str] = None
    subjects: Optional[List[str]] = Field(sa_type=JSONB, default_factory=list)
    difficulty: Optional[int] = None

class CourseBaseExtended(CourseBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class Course(CourseBaseExtended, table=True):
    pass

class CourseCreate(CourseBaseExtended):
    pass

class CourseRead(CourseBaseExtended):
    pass

class CourseReadVerbose(CourseBaseExtended):
    pass

class CourseFilter(BaseModel):
    name: Optional[str] = None
    instructor: Optional[str] = None
    quarter: Optional[date] = None
    quarter_filter: Optional[Literal["equal", "newer", "older", "newer-inclusive", "older-inclusive"]] = None
    subjects: Optional[List[str]] = None
    difficulty: Optional[int] = None

class CourseUpdate(CourseBase):
    name: Optional[str] = None
    instructor: Optional[str] = None
    quarter: Optional[date] = None
    summary: Optional[str] = None
    subjects: Optional[List[str]] = None
