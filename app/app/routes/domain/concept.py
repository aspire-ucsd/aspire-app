from typing import List, Union, Dict

from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import JSONResponse

from app.app.errors.db_error import DBError
from app.domain.models.errors import ErrorResponse

from app.domain.models.forms import ListOfCollectionIds, list_collection_ids

from app.domain.models.concept import ConceptCreate, ConceptCreateBulkRead, ConceptRead, ConceptFilter, ConceptReadVerbose, ConceptReadPreformatted
from app.domain.protocols.services.concept import ConceptService as ConceptServiceProtocol
from app.domain.services.concept import ConceptService

from fastapi_lti1p3 import enforce_auth

router = APIRouter()

# @router.post("/add", name="concept:add-concept", response_model=Union[ConceptRead, ErrorResponse])
# async def add_concept(
#     request: Request,
#     response: Response,
#     concept: ConceptCreate,
#     concept_service: ConceptServiceProtocol = Depends(ConceptService)
#     ) -> Union[ConceptRead, ErrorResponse]:
#     """
#     Adds a single concept to the DB
#     """
#     try:
#         return await concept_service.create_concept(concept=concept)
    
#     except DBError as e:
#         response.status_code = e.status_code
#         return ErrorResponse(
#             code=e.status_code,
#             type=e.type,
#             message=str(e)
#         )


# @router.post("", name="Concept:add-concepts", response_model=Union[ConceptCreateBulkRead, ErrorResponse])
# async def add_concepts(
#     request: Request,
#     response: Response,
#     concepts: List[ConceptCreate],
#     concept_service: ConceptServiceProtocol = Depends(ConceptService)
#     ) -> Union[ConceptCreateBulkRead,ErrorResponse]:
#     """
#     Adds one or many concepts to the DB and assigns them to a course and domain
#     """
#     try:
#         return await concept_service.bulk_create_concepts(concepts=concepts)
    
#     except DBError as e:
#         response.status_code = e.status_code
#         return ErrorResponse(
#             code=e.status_code,
#             type=e.type,
#             message=str(e)
#         )


# @router.get("/one/{concept_name}", name="Concept:get-concepts", response_model=Union[ConceptReadVerbose, ErrorResponse])
# async def get_concept(
#     request: Request, 
#     response: Response,
#     concept_name: str,
#     concept_service: ConceptServiceProtocol = Depends(ConceptService)
#     ) -> Union[ConceptReadVerbose, ErrorResponse]:
#     """
#     Returns the details of a specific concept
#     """
#     try:
#         return await concept_service.get_concept(concept_name=concept_name, read_mode="verbose")
    
#     except DBError as e:
#         response.status_code = e.status_code
#         return ErrorResponse(
#             code=e.status_code,
#             type=e.type,
#             message=str(e)
#         )


@router.get("/filter", name="Concept:get-concepts-by-filter", response_model=Union[List[ConceptReadVerbose], ErrorResponse])
async def get_concept_filtered(
    request: Request, 
    response: Response,
    filter: ConceptFilter = Depends(ConceptFilter),
    concept_service: ConceptServiceProtocol = Depends(ConceptService)
    ) -> Union[List[ConceptReadVerbose], ErrorResponse]:
    """
    Returns all concepts matching the supplied filters
    """
    try:
        return await concept_service.get_many_concepts(filters=filter, read_mode="verbose")
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )


# @router.get("/from_modules", name="Concept:get-all-concepts-of-modules", response_model=Dict[str, ConceptReadPreformatted])
# async def get_concepts_from_modules(
#     request: Request,
#     module_ids: ListOfModuleIds = Depends(list_module_ids),
#     concept_service: ConceptServiceProtocol = Depends(ConceptService)
#     ):
#     """
#     Returns a prepackaged collection of concepts belonging to all supplied modules the client is authorized to access, structured for use within a domain editor/visualizer
#     """
#     session_data, _ = await enforce_auth(request=request)
#     course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")
    
#     results = await concept_service.get_all_concepts_from_modules(course_id=course_id, module_ids=set(module_ids.ids))
#     return results
