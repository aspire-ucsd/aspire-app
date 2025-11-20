
from typing import Union

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
)

from fastapi_lti1p3 import enforce_auth

from app.domain.models.errors import ErrorResponse
from app.domain.protocols.services.course import CourseService as CourseServiceProtocol
from app.domain.services.course import CourseService
from app.domain.models.course import CourseUpdate, CourseReadVerbose

from app.app.errors.db_error import DBError


router = APIRouter()

#TODO: Enforce auth

@router.put("/{course_id}", name="Course:update-course", response_model=Union[CourseReadVerbose, ErrorResponse])
async def update_course(
    request: Request, 
    response: Response,
    course_id: int,
    course_update: CourseUpdate,
    course_service: CourseServiceProtocol = Depends(CourseService)
    ) -> Union[CourseReadVerbose, ErrorResponse]:
    """
    Updates a Course
    """
    try:
        return await course_service.update_course(course_id=course_id, course_update=course_update)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    
#TODO: Add return for success or failure to delete
@router.delete("/{course_id}", name="Course:delete-course")
async def delete_course(
    request: Request, 
    response: Response,
    course_id: int,
    course_service: CourseServiceProtocol = Depends(CourseService)
    ):
    """
    Deletes a course and all corresponding relationships
    """
    try:
        return await course_service.delete_course(course_id=course_id)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )