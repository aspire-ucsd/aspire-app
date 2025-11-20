from typing import  List, Union

from fastapi import APIRouter, Depends, Response, Request

from app.app.errors.db_error import DBError

from app.domain.models.errors import ErrorResponse

from app.utils.permissions import SMEInclusive

from app.domain.models.errors import ErrorResponse
from app.domain.protocols.services.course import CourseService as CourseServiceProtocol
from app.domain.services.course import CourseService
from app.domain.models.course import CourseFilter, CourseReadVerbose


from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.errors import AuthValidationError

router = APIRouter()

@router.get("/courses/{course_filter}")
async def course_template_list(
    request: Request, 
    response: Response,
    course_filter: CourseFilter = Depends(CourseFilter),
    course_service: CourseServiceProtocol = Depends(CourseService)
    ) -> Union[list[CourseReadVerbose], ErrorResponse]:
    """
    Returns a list of course templates, used when selecting an existing course to build a new one off of.
    """
    #TODO: Update logic to match new usecase
    try:
        return await course_service.get_matching_courses(filters=course_filter)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )


@router.get("/course/{course_id}")
async def course_template_detailed_view(
    request: Request, 
    response: Response,
    course_id: int,
    course_service: CourseServiceProtocol = Depends(CourseService)
) -> Union[CourseReadVerbose, ErrorResponse]:
    """
    Returns a a detailed view of a course including concepts and collections. 
    Used when selecting an existing course to build a new one off of.
    """
    #TODO: Update logic to match new usecase
    try:
        return await course_service.get_one_course(course_id=course_id, read_mode="verbose")
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )