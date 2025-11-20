from mimetypes import guess_type
from typing import List, Literal, Union

from fastapi import (
    APIRouter,
    Depends,
    File,
    Request,
    Response,
    UploadFile,
)


from app.domain.models.errors import ErrorResponse
from app.domain.models.forms import RegistrationForm


from app.domain.models.course import CourseRead, CourseCreate
from app.domain.protocols.services.course import CourseService as CourseServiceProtocol
from app.domain.services.course import CourseService


from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.session_cache import SessionCache

from app.app.errors.db_error import DBError


router = APIRouter()

@router.post("/register/new", name="qas:register-new-course", response_model=Union[CourseRead, ErrorResponse])
async def register(
    request: Request,
    response: Response,
    model_name: Literal["gpt-3.5-turbo", "gemini-1.5-pro-latest", "gpt-4o", "llama-3"],
    content_files: List[UploadFile] = File(...),
    form_data: RegistrationForm = Depends(RegistrationForm.as_form),
    course_service: CourseServiceProtocol = Depends(CourseService)
) -> Union[CourseRead, ErrorResponse]:
    #TODO: update docstring
    """
    If course_summary not provided, llm will generate one from content files
    """
    #TODO: Add system for reusing existing courses as templates
    # Check if files are either text or PDF
    for content_file in content_files:
        mimetype, _ = guess_type(content_file.filename)
        if mimetype not in ['text/plain', 'application/pdf']:
            response.status_code = 400
            return ErrorResponse(code=400, detail="Invalid file type. Only text and PDF are allowed.")
    try:
        session_data = await enforce_auth(request=request)
        course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")

        course_create = CourseCreate(**form_data, id=course_id)
        course_result = await course_service.create_course(course_create=course_create, content_files=content_files, model_name=model_name)
        if isinstance(course_result, ErrorResponse):
            response.status_code = course_result.code
            return course_result

        return course_result
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    
@router.post("/register/template", name="register-new-course-from-template")
async def register_from_template(course_id:int):
    pass