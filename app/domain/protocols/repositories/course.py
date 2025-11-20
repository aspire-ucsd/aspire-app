from typing import List, Optional, Protocol, Union, Literal

from app.domain.models.errors import ErrorResponse
from app.domain.models.course import CourseRead, CourseCreate, CourseFilter, CourseUpdate, CourseReadVerbose

class CourseRepository(Protocol):
    async def add(self, course: CourseCreate) -> CourseRead:
        """
        Adds a course to the DB
        """
        ...

    async def get_one(self, course_id: int, read_mode: Literal["normal", "verbose"] = "normal") -> Union[CourseRead, CourseReadVerbose]:
        """
        Returns a course filtered by its course_id. 
        :param course_id: the id of the course being selected
        :param read_mode: ('normal', 'verbose') in 'normal' mode returns the domain_id and course_id, in 'verbose' mode returns all the details of the course
        """
        ...

    async def get_many(self, filters: CourseFilter) -> List[CourseReadVerbose]:
        """
        Returns all courses matching filters
        :param filters: Optional filtering params, returns all courses matching each param 
            - name: Optional[str] - The name of the course
            - instructor: Optional[str] - The instructor assigned to the course
            - quarter: Optional[date] - The quarter the course started on
            - quarter_filter: Optional[Literal["equal", "newer", "older", "newer-inclusive", "older-inclusive"]] - Defaults to 'equal' 
            Specifies whether matching courses should be older, newer, or equal to the filter date, inclusive will retain courses equal to the filter date as well.
            - subject: Optional[str] - The course subject
            - difficulty: Optional[int] - The course difficulty
        """
        ...

    async def update(self, course_id: int, course_update: CourseUpdate) -> CourseReadVerbose:
        ...

    async def delete(self, course_id: int):
        ...