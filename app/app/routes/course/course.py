from typing import Union

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
)

from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.errors import AuthValidationError, SessionExpiredError

from app.domain.models.errors import ErrorResponse
from app.domain.protocols.services.course import CourseService as CourseServiceProtocol
from app.domain.services.course import CourseService
from app.domain.models.course import CourseCreate, CourseRead

from app.domain.models.concept import  ConceptRead
from app.domain.protocols.services.concept import ConceptService as ConceptServiceProtocol, ConceptToConceptService as CToCServiceProtocol
from app.domain.services.concept import ConceptService

from app.domain.protocols.services.concept_collection import CollectionService as CollectionServiceProtocol
from app.domain.services.concept_collection import CollectionService

from app.app.errors.db_error import DBError
from app.domain.models.forms import RegistrationForm

from app.domain.models.course_domain import CourseDomain


router = APIRouter()


@router.post("/register/new", name="qas:register-new-course", response_model=Union[CourseRead, ErrorResponse])
async def register(
    request: Request,
    response: Response,
    form_data: RegistrationForm = Depends(RegistrationForm.as_form),
    course_service: CourseServiceProtocol = Depends(CourseService)
) -> Union[CourseRead, ErrorResponse]:
    #TODO: update docstring
    """
    """
    #TODO: Add system for reusing existing courses as templates
    # Check if files are either text or PDF
    try:
        session_data = await enforce_auth(request=request)
        course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")

        course_create = CourseCreate(**form_data, id=course_id)
        course_result = await course_service.create_course(course_create=course_create)

        return course_result
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    
    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )
    
@router.post("/register/template", name="register-new-course-from-template")
async def register_from_template(course_id:int):
    pass


@router.get("/domain", name="Course:get-course-domain", response_model=Union[CourseDomain, ErrorResponse])
async def get_course_domain(
    request: Request,
    response: Response,
    concept_service: Union[ConceptServiceProtocol, CToCServiceProtocol] = Depends(ConceptService),
    collection_service: CollectionServiceProtocol = Depends(CollectionService),
    ) -> CourseDomain:
    """
    Returns a prepackaged collection of concepts, junctions, and collections belonging to a course
    """
    #TODO: update logic to follow new operational flow
    try:
        session_data = await enforce_auth(request=request)
        course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")

    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )
    
    try:
        collections = await collection_service.get_course_collections(course_id=course_id)
        collection_ids = {item.id for item in collections}
    except DBError as e:
        return CourseDomain()
    
    try:
        concepts = await concept_service.get_all_concepts_from_collections(course_id=course_id, collection_ids=collection_ids)
    except DBError as e:
        return CourseDomain(collections=collections)
    
    try:
        concept_read_list = [ConceptRead(name=item.name) for item in concepts.values()]
        junctions = await concept_service.get_concept_junctions(concepts=concept_read_list)
        # TODO: modify concept_service.get_concept_junctions to have an option for excluding edges where the source and the target are not contained in the concept list
        concept_read_list = [item.name for item in concept_read_list]
        junctions = [item for item in junctions if item.concept_name in concept_read_list and item.prereq_name in concept_read_list]

    except DBError as e:
        return CourseDomain(collections=collections)
    
    return CourseDomain(collections=collections, concepts=concepts, junctions=junctions)
    


