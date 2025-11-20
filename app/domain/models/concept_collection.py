import enum
from typing import Optional, List

from sqlmodel import Field, SQLModel, ForeignKey, Column, Integer, Enum

class CollectionTypes(str, enum.Enum):
    module = "module"
    container = "container"

class ConceptCollectionBase(SQLModel):
    label: str = Field(max_length=255)
    content_summary: Optional[str] = None
    type: CollectionTypes = Field(sa_column=Column(Enum(CollectionTypes)))
    order: Optional[int] = None


class ConceptCollectionBaseExtended(ConceptCollectionBase):
    course_id: int = Field(foreign_key="course.id", ondelete="CASCADE")

class ConceptCollection(ConceptCollectionBaseExtended, table=True):
    __tablename__ = "concept_collection"
    id: Optional[int] = Field(default=None, primary_key=True)


class CollectionCreate(ConceptCollectionBase):
    pass

class CollectionCreateExtended(ConceptCollectionBaseExtended):
    pass

class CollectionRead(ConceptCollection):
    pass

class CollectionUpdate(SQLModel):
    title: Optional[str] = None
    content_summary: Optional[str] = None

class CollectionSummary(SQLModel):
    summary: str