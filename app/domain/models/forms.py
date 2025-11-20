from typing import Optional
from datetime import date
from fastapi import Form, HTTPException, Query

from pydantic import BaseModel, ValidationError
from app.domain.models.concept import ConceptBulkRead, ConceptRead

class RegistrationForm(BaseModel):
    instructor: str = Form(...),
    quarter: date = Form(...),
    course_name: Optional[str] = Form(None),
    course_summary: Optional[str] = Form(None)
    subject: str = Form(...),
    difficulty: int = Form(...),
    
    @classmethod
    def as_form(
        cls,
        instructor: str = Form(...),
        quarter: date = Form(...),
        course_name: Optional[str] = Form(None),
        subject: str = Form(...),
        difficulty: int = Form(...),
    ):
        name = name if name != None else f"{instructor} - {quarter}"
        return cls(instructor=instructor, quarter=quarter, course_name=course_name, subject=subject, difficulty=difficulty)
    

class ModuleForm(BaseModel):
    title: str = Form(...),
    course_id: int = Form(...)

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        course_id: int = Form(...)
    ):
        return cls(title=title, course_id=course_id)


class ListOfCollectionIds(BaseModel):
    ids: list[int] = None


def list_collection_ids(list_of_ids: str):
    try:
        ids = ListOfCollectionIds(ids=list_of_ids.split(","))
    except ValidationError:
        raise HTTPException(400, "IDs must be valid integers.")
    return ids


def list_concept_names(list_of_names: str=Query(
        ..., 
        description="Multiple names must be delimited by '|' (e.g, 'value 1|value 2|value 3)",
        )
    ) -> ConceptBulkRead:
    try:
        ids = ConceptBulkRead(concepts=[ConceptRead(name=name) for name in list_of_names.split("|")])
    except ValidationError:
        raise HTTPException(400, "IDs must be valid strings and delimited with '|' if multiple names are provided.")
    return ids