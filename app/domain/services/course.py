from typing import  List, Union, Literal
from fastapi import Depends

from app.domain.protocols.services.course import CourseService as CourseServiceProtocol
from app.domain.protocols.services.concept import ConceptService as ConceptServiceProtocol

from app.domain.protocols.repositories.course import CourseRepository as CourseRepoProtocol

from app.infrastructure.database.repositories.course import CourseRepository

from app.domain.services.concept import ConceptService

from app.domain.models.course import CourseRead, CourseCreate, CourseCreate, CourseUpdate, CourseFilter, CourseReadVerbose
from app.domain.models.llm_agent import Validator, ContingencyFunctions

from app.infrastructure.LLM.llm_agent import LLMAgent
from app.infrastructure.LLM.contingencies.general import check_valid_json
from app.infrastructure.LLM.contingencies.summarize import format_as_string

class CourseService(CourseServiceProtocol):
    def __init__(
            self, 
            course_repo: CourseRepoProtocol = Depends(CourseRepository),
            concept_service: ConceptServiceProtocol = Depends(ConceptService),

    ):
        self.course_repo = course_repo
        self.concept_service = concept_service

    async def create_course(self, course_create: CourseCreate) -> CourseRead:
        return await self.course_repo.add(course=course_create)

    async def get_one_course(self, course_id: int, read_mode: Literal["normal", "verbose"] = "normal") -> Union[CourseRead, CourseReadVerbose]:
        return await self.course_repo.get_one(course_id=course_id, read_mode=read_mode)


    async def get_matching_courses(self, filters: CourseFilter) -> List[CourseReadVerbose]:
        return await self.course_repo.get_many(filters=filters)


    async def update_course(self, course_id: int, course_update: CourseUpdate) -> CourseReadVerbose:
        return await self.course_repo.update(course_id=course_id, course_update=course_update)


    async def delete_course(self, course_id: int):
        return await self.course_repo.delete(course_id=course_id)