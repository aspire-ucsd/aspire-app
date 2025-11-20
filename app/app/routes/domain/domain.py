from typing import  List, Union

from fastapi import APIRouter, Depends, Response, Request

from app.app.errors.db_error import DBError

from app.domain.models.errors import ErrorResponse

from app.utils.permissions import SMEInclusive
from app.domain.protocols.services.domain import DomainService as DomainServiceProtocol
from app.domain.services.domain import DomainService

from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.errors import AuthValidationError

router = APIRouter()

@router.get('/subjects')
async def get_used_subjects(
    response: Response,
    domain_service: DomainServiceProtocol = Depends(DomainService)
    ) -> List[str]:
    try:
        return await domain_service.get_all_subjects()
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )