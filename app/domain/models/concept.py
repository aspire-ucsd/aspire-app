from typing import Optional, List, Union
from sqlmodel import Field, SQLModel, Column, VARCHAR, Integer
from sqlalchemy import ForeignKey, Column
from pydantic import field_validator

from .errors import DBError


class ConceptBase(SQLModel):
    name: str = Field(
        max_length=255, 
        regex=r"^[^|]+$", 
        description="The name of a unique concept, cannot include '|' for delimitation purposes.",
        sa_column=Column("name", VARCHAR, unique=True, primary_key=True))
    
    @field_validator("name", mode="before")
    def enforce_title_case(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        return value.title()

class ConceptBaseExtended(SQLModel):
    subject: str
    difficulty: int
    summary: Optional[str]

class Concept(ConceptBase, ConceptBaseExtended, table=True):
    pass

class ConceptCreate(ConceptBase, ConceptBaseExtended):
    pass

class ConceptRead(ConceptBase):
    pass

class ConceptReadVerbose(ConceptBase, ConceptBaseExtended):
    pass

class ConceptReadPreformatted(ConceptReadVerbose):
    id: str
    module: List[int] 
    is_saved: bool = True
    params: dict = {}


class ConceptCreateBulkRead(SQLModel):
    success: Union[List[ConceptRead], None]
    failed: Union[List[DBError], None]

class ConceptBulkRead(SQLModel):
    concepts: List[ConceptRead]

class ConceptFilter(SQLModel):
    course_id: Optional[int] = None
    subjects: Optional[str] = Field(default=None, description="For multiple subjects, use '|' deliminator between values")
    difficulty: Optional[int] = None
    module_id: Optional[int] = None

class ConceptFilterByCourse(SQLModel):
    course_id: int
    subject: bool=False
    difficulty: bool=False

class ConceptToConceptBase(SQLModel):
    concept_name: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True
        ),
        alias="target",
    )
    prereq_name: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True
        ),
        alias="source",
    )
    @field_validator("concept_name", "prereq_name", mode="before")
    def enforce_title_case(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("concept_name must be a string.")
        return value.title()


class ConceptToConcept(ConceptToConceptBase, table=True):
    __tablename__ = ("concept_to_concept")
    pass

class ConceptToConceptCreate(ConceptToConceptBase):
    pass

class ConceptToConceptRead(ConceptToConceptBase):
    pass

class ConceptToConceptDelete(ConceptToConceptBase):
    pass


class ConceptToCollectionBase(SQLModel):
    concept_name: str = Field(
        sa_column=Column(
            VARCHAR,
            ForeignKey("concept.name", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True
        )
    )
    collection_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("concept_collection.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True
        )
    )
    @field_validator("concept_name", mode="before")
    def enforce_title_case(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("concept_name must be a string.")
        return value.title()

class ConceptToCollection(ConceptToCollectionBase, table=True):
    __tablename__ = "concept_to_collection"


class ConceptToCollectionCreate(ConceptToCollectionBase):
    pass

class ConceptToCollectionRead(ConceptToCollectionBase):
    pass

class ConceptToCollectionDelete(ConceptToCollectionBase):
    pass