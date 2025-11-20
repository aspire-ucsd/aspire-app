from typing import  List, Union

from fastapi import APIRouter, Depends, Response, Request

from app.app.errors.db_error import DBError

from app.domain.models.errors import ErrorResponse

from app.utils.permissions import SMEInclusive

from app.domain.models.concept_collection import CollectionRead, CollectionUpdate, CollectionCreate, CollectionCreateExtended
from app.domain.services.concept_collection import CollectionService
from app.domain.protocols.services.concept_collection import CollectionService as CollectionServiceProtocol


from app.domain.models.concept import ConceptToCollectionCreate, ConceptToCollectionDelete, ConceptToCollectionRead, ConceptBulkRead
from app.domain.protocols.services.concept_collection import CollectionService as CToCcServiceProtocol
from app.domain.services.concept import ConceptService

from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.errors import AuthValidationError, SessionExpiredError

router = APIRouter()

@router.post("", name="Collection:create-collection", response_model=Union[CollectionRead, ErrorResponse])
async def create_collection(
    request: Request, 
    response: Response,
    collection: CollectionCreate,
    collection_service: CollectionServiceProtocol = Depends(CollectionService)
    ) -> Union[CollectionRead, ErrorResponse]:
    """
    Creates a new, empty collection and adds it to the users active course
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")

    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type="AuthValidationError",
            message=e.message
        )
    
    try:
        collection = CollectionCreateExtended(**collection.model_dump(), course_id=course_id)
        return await collection_service.create_collection(collection=collection)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

@router.get("/{collection_id}", name="Collection:get-collection", response_model=Union[CollectionRead, ErrorResponse])
async def get_collection(
    response: Response,
    collection_id: int,
    collection_service: CollectionServiceProtocol = Depends(CollectionService)
    ) -> Union[CollectionRead, ErrorResponse]:
    """
    Returns a single collection by its ID
    """
    try:
        return await collection_service.get_collection(collection_id=collection_id)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

@router.get("/course", name="Collection:get-all-collections-of-course", response_model=Union[List[CollectionRead], ErrorResponse])
async def get_all_course_collections(
    request: Request, 
    response: Response,
    collection_service: CollectionServiceProtocol = Depends(CollectionService)
    ) -> Union[List[CollectionRead], ErrorResponse]:
    """
    Returns all collections bellonging to a course
    """
    session_data = await enforce_auth(request=request)
    course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")
    try:
        return await collection_service.get_course_collections(course_id=course_id)

    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

@router.put("/{collection_id}", name="Collection:update-collection", response_model=Union[CollectionRead, ErrorResponse])
async def update_collection(
    request: Request, 
    response: Response,
    collection_id: int,
    collection_update: CollectionUpdate,
    collection_service: CollectionServiceProtocol = Depends(CollectionService)
    ) -> Union[CollectionRead, ErrorResponse]:
    """
    Updates a collection to match the supplied CollectionUpdate object.
    """
    try:
        await enforce_auth(request=request, accepted_roles=SMEInclusive())

    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type="AuthValidationError",
            message=e.message
        )
    
    try:
        return await collection_service.update_collection(collection_id=collection_id, collection_update=collection_update)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

@router.delete("/{collection_id}", name="Collection:delete-collection-from-course")
async def delete_collection_from_own_course(
    request: Request, 
    response: Response,
    collection_id: int,
    collection_service: CollectionServiceProtocol = Depends(CollectionService)
    ):
    """
    Removes a collection from the active course
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")

    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type="AuthValidationError",
            message=e.message
        )
    
    try:
        return await collection_service.delete_collection_from_course(collection_id=collection_id, course_id=course_id)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    
@router.post("/concept", name="Concept-to-Collection:create-concept-to-module-junction", response_model=Union[List[ConceptToCollectionRead], ErrorResponse])
async def create_concept_to_collection_junction(
    request: Request, 
    response: Response,
    junctions: List[ConceptToCollectionCreate],
    c_to_cc_service: CToCcServiceProtocol = Depends(ConceptService)
    ) -> Union[List[ConceptToCollectionRead], ErrorResponse]:
    """
    Creates a new Concept-to-Collection Junction
    """
    try:
        return await c_to_cc_service.bulk_create_module_junctions(junctions=junctions)

    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

@router.get("/{collection_id}/concepts", name="Concept-to-Collection:get-all-collection-concepts", response_model=Union[ConceptBulkRead, ErrorResponse])
async def get_collection_concepts(
    request: Request, 
    response: Response,
    collection_id: int,
    c_to_cc_service: CToCcServiceProtocol = Depends(ConceptService)
    ) -> Union[ConceptBulkRead, ErrorResponse]:
    """
    Returns all concepts belonging to a collection
    """
    try:
        return await c_to_cc_service.get_all_concepts_in_module(module_id=collection_id)

    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

@router.delete("", name="Concept-to-Collection:remove-concept-from-collection")
async def remove_collection_concept(
    request: Request, 
    response: Response,
    junctions: List[ConceptToCollectionDelete],
    c_to_cc_service: CToCcServiceProtocol = Depends(ConceptService)
    ) -> None:
    """
    Removes a concept from a module
    """
    try:
        await c_to_cc_service.delete_module_junctions(junctions=junctions)

    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )

    