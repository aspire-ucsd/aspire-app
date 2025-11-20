from typing import List, Optional, Protocol, Literal, Union
from fastapi import UploadFile

from app.domain.models.course import CourseRead, CourseCreate, CourseFilter, CourseUpdate, CourseReadVerbose

class CourseService(Protocol):
    async def create_course(self, course_create: CourseCreate) -> CourseRead:
        ...

    async def get_one_course(self, course_id: int, read_mode: Literal["normal", "verbose"] = "normal") -> Union[CourseRead, CourseReadVerbose]:
        ...

    async def get_matching_courses(self, filters: CourseFilter) -> List[CourseReadVerbose]:
        ...

    async def update_course(self, course_id: int, course_update: CourseUpdate) -> CourseReadVerbose:
        ...

    async def delete_course(self, course_id: int):
        ...