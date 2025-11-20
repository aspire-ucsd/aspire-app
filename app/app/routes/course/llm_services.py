import json
from mimetypes import guess_type
from typing import List, Literal,  Union, Optional
from pydantic import ValidationError
from fastapi import (
    APIRouter,
    Depends,
    File,
    Request,
    Response,
    UploadFile,
    BackgroundTasks,
)

from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.errors import AuthValidationError, SessionExpiredError

from app.domain.models.errors import ErrorResponse


from app.domain.services.concept import ConceptService, ConceptServiceProtocol
from app.domain.models.concept import ConceptFilter, ConceptCreate

from app.domain.protocols.services.change_requests import ChangeRequestService as VQServiceProtocol
from app.domain.services.change_requests import ChangeRequestService
from app.domain.models.change_requests import ChangeRequestCreateClient, ValidationStatusEnum

from app.domain.models.course import CourseRead

from app.aspire_llm_agent.services.domain_authoring import identify_concepts_in_batches
from app.aspire_llm_agent.utils import get_files_from_url, split_docs, concept_document_enricher

from app.app.errors.db_error import DBError

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/summarize", name="Course-LLM-Services:summarize-course", response_model=Union[CourseRead, ErrorResponse])
async def summarize_course(
    request: Request,
    response: Response,
    model_name: Literal["gpt-3.5-turbo", "gemini-1.5-pro-latest", "gpt-4o", "llama-3"],
    client_input: Optional[str] = None,
    content_files: Optional[List[UploadFile]] = File(...),
) -> Union[str, ErrorResponse]:
    
    for content_file in content_files:
        mimetype, _ = guess_type(content_file.filename)
        if mimetype not in ['text/plain', 'application/pdf']:
            response.status_code = 400
            return ErrorResponse(code=400, detail="Invalid file type. Only text and PDF are allowed.")


@router.post("/module/concepts", name="Course-LLM-Services:Generate-Module-Concepts")
async def generate_module_concepts(
    request: Request, 
    response: Response,
    source_locations: List[str],
    module_id: int,
    background_tasks: BackgroundTasks,
    concept_service: ConceptServiceProtocol = Depends(ConceptService),
    validation_service: VQServiceProtocol = Depends(ChangeRequestService)
):
    try:
        session_data = await enforce_auth(request=request)

    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )
    
    course_id = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("course_id")
    course_summary = session_data.course_metadata.get("summary")
    course_subject = session_data.course_metadata.get("subject")


    async def concept_retreiver_func(params: dict):
        results = await concept_service.get_many_concepts(filters=ConceptFilter(subject=params.get("course_subject")), read_mode="verbose")
        return results

    async def storage_method(results: dict, extra_params: dict):
        try:
            results = json.loads(results.get('output_text'))

        except json.JSONDecodeError as e:
            #TODO: handle llm output decode errors, should be rare due to programatic operation of combine/collapse chain
            logger.exception(msg="Failed to parse llm json output")
        
        name_filterable_concepts = {item.get("name"): item for item in results if item.get("name")}

        exists_check = await concept_service.check_if_concepts_exist(concept_names=list(name_filterable_concepts.keys()))
        module_id = extra_params.get("module_id")

        matched_concepts = exists_check.get("matched_concepts")
        unmatched_concepts = exists_check.get("unmatched_concepts")

        validation_request_list = []

        if matched_concepts:
            for concept in matched_concepts:
                try:
                    #Validates datstructure conforms to standard ConceptCreate format
                    concept_full = ConceptCreate(**name_filterable_concepts[concept])

                    validation_request_list.append(ChangeRequestCreateClient(
                        entity_id=concept,
                        is_from_llm=True,
                        post_approval_procedure={'type': 'junction', 'target_table': 'module', 'target_id': module_id},
                        entity_type="concept",
                        entity_data=concept_full.model_dump(),
                        validation_status=ValidationStatusEnum.draft
                    ))
                
                except ValidationError as e:
                    logger.warn(msg=f"Validation request data format invalid, expected concept object, received: {name_filterable_concepts[concept]}")
                    continue

                if len(validation_request_list) > 50:
                    # allows intermittent processing of data for large outputs
                    try:
                        await validation_service.bulk_add_items(items=validation_request_list, client_session=extra_params.get("client_session"))
                        validation_request_list = []

                    except DBError as e:
                        logger.warn(msg="failed to save batch of validation requests")
                        continue


        if unmatched_concepts:
            for concept in unmatched_concepts:
                try:
                    #Validates datstructure conforms to standard ConceptCreate format
                    concept_full = ConceptCreate(**name_filterable_concepts[concept])

                    validation_request_list.append(ChangeRequestCreateClient(
                        is_from_llm=True,
                        post_approval_procedure={'type': 'junction', 'target_table': 'module', 'target_id': module_id},
                        entity_type="concept",
                        modification_type="create",
                        entity_data=concept_full.model_dump(),
                        validation_status=ValidationStatusEnum.draft
                    ))
                
                except ValidationError as e:
                    logger.warn(msg=f"Validation request data format invalid, expected concept object, received: {name_filterable_concepts[concept]}")
                    continue

                if len(validation_request_list) > 50:
                    # allows intermittent processing of data for large outputs
                    try:
                        await validation_service.bulk_add_items(items=validation_request_list, client_session=extra_params.get("client_session"))
                        validation_request_list = []

                    except DBError as e:
                        logger.warn(msg="failed to save batch of validation requests")
                        continue
        try:
            #stores any stragglers after the loops complete
            if validation_request_list:
                await validation_service.bulk_add_items(items=validation_request_list, client_session=extra_params.get("client_session"))
            
        except DBError as e:
            logger.warn(msg="failed to save batch of validation requests")
            



    background_tasks.add_task(
        identify_concepts_in_batches, 
        source_locations=source_locations, 
        course_subjects=[course_subject], 
        course_summary=course_summary,
        storage_method=storage_method,
        document_loader=get_files_from_url,
        document_splitter=split_docs,
        document_enricher=concept_document_enricher,
        extra_params={
            "course_id": course_id, 
            "module_id": module_id,
            "storage_type": "module-concepts",
            "canvas_api_key": "4A3H773hy4fCCTvuuHhBk7rCP2muXRA2eczPyW3cn8uGhYGEexVYTBCRQeWxc6eT",
            "concept_retreiver_func": concept_retreiver_func,
            "course_subject": course_subject,
            "client_session": session_data
            }
        )
    
    response.status_code = 200
    return {"message": "Concept Identification Initialized"}



