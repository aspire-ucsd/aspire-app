from typing import  List, Union, Literal
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, Response, Request

from app.app.errors.db_error import DBError
from app.app.errors.validation_error import ValidationError

from app.domain.models.errors import ErrorResponse

from app.utils.permissions import SMEInclusive

from app.domain.models.errors import ErrorResponse
from app.domain.models.change_requests import ChangeRequestRead, ChangeRequestCreateClient, Comment, ChangeRequestUpdate
from app.domain.protocols.services.change_requests import ChangeRequestService as ChangeRequestServiceProtocol
from app.domain.services.change_requests import ChangeRequestService

from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.errors import AuthValidationError, SessionExpiredError

router = APIRouter()

@router.get("/queue")
async def get_client_queue(
    request: Request, 
    response: Response,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, list, ErrorResponse]:
    """
    Returns a list of change_request entries relevant to the user
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.get_relevant_items(client_session=session_data)
    
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
    
@router.get("/closed")
async def get_client_closed(
    request: Request, 
    response: Response,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, list, ErrorResponse]:
    """
    Returns a list of closed change_request entries relevant to the user
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.get_my_closed_requests(client_session=session_data)
    
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

@router.get("/drafts")
async def get_client_drafts(
    request: Request, 
    response: Response,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, list, ErrorResponse]:
    """
    Returns a list of change_request draft entries relevant to the user
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.get_my_drafts(client_session=session_data)
    
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
    
@router.post("")
async def add_change_request(
    request: Request, 
    response: Response,
    change_request: ChangeRequestCreateClient,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, ErrorResponse]:
    """
    Create a new change request
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.add_item(item=change_request, client_session=session_data)
    
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
    
@router.put("/vote")
async def add_vote(
    request: Request, 
    response: Response,
    request_id: int,
    vote: Literal["approved", "rejected"],
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, ErrorResponse]:
    """
    Adds users vote to change request
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        client_id = session_data.user_credentials.internal_id
        comment_type_map = {"approved": "approve_vote", "rejected": "reject_vote"}
        print(f"\n\nClient ID: {client_id}\n\n")
        update = ChangeRequestUpdate(
            id=request_id, 
            votes=[vote], 
            reviewers=[client_id],
            comments=[
                Comment(
                    type=comment_type_map[vote],
                    content=f"msg|Change Request {vote} by user.",
                    submitted_by=client_id
                    )
                ]
            )
        return await change_request_service.update_item(update=update)
    
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

@router.put("/comment")
async def add_comment(
    request: Request, 
    response: Response,
    request_id: int,
    comment: Comment,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, ErrorResponse]:
    """
    Adds users comment to change request
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        client_id = session_data.user_credentials.internal_id

        comment.submitted_by = client_id
        update = ChangeRequestUpdate(id=request_id, comments=[comment])

        return await change_request_service.update_item(update=update)
    
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

@router.put("/status")
async def update_status(
    request: Request, 
    response: Response,
    change_request_id: int,
    status: Literal["pending", "approved", "rejected", "draft"] = "pending",
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, list, ErrorResponse]:
    """
    Updates the validation status of a change request, additional changes or actions required upon changing validation status are automatically applied.
    In all cases votes are reset and a comment noting the status update and prior vote is added.

    Updating a CR to 'pending' automatically assigns reviewers, and a closing time.

    Updating a CR to 'draft' automatically clears all reviewers and the closing time.

    Updating a CR to 'approved' automatically promotes the CR to the db, adds the reviewer and commit time, and clears all reviewers and the closing time.

    Updating a CR to 'rejected' clears all reviewers and the closing time, adds the commit time.
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.update_status(client_session=session_data, change_request_id=change_request_id, status=status)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    except (AuthValidationError, SessionExpiredError, ValidationError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )

@router.put("")
async def update_entity_data(
    request: Request, 
    response: Response,
    change_request_id: int,
    entity_data: dict,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, list, ErrorResponse]:
    """
    Updates the entity data of a Change Request owned by the client and logs the old entity data as a comment
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.update_data(client_session=session_data, change_request_id=change_request_id, entity_data=entity_data)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    except (AuthValidationError, ValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )

@router.put("/close")
async def close_change_request(    
    request: Request, 
    response: Response,
    change_request_id: int,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> Union[ChangeRequestRead, list, ErrorResponse]:
    """
    Updates the entity data of a Change Request owned by the client and logs the old entity data as a comment
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.close_request(change_request_id=change_request_id, client_session=session_data)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    except (AuthValidationError, ValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )

@router.delete("/draft")
async def delete_client_draft(
    request: Request, 
    response: Response,
    change_request_id: int,
    change_request_service: ChangeRequestServiceProtocol = Depends(ChangeRequestService)
    ) -> None:
    """
    Deletes a Change Request draft owned by the user
    """
    try:
        session_data = await enforce_auth(request=request, accepted_roles=SMEInclusive())
        return await change_request_service.delete_draft(client_session=session_data, change_request_id=change_request_id)
    
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
    
