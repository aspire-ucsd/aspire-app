from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.templating import Jinja2Templates

from app.domain.models.errors import ErrorResponse
from app.app.errors.db_error import DBError
from app.config.environment import get_settings

from app.domain.services.course import CourseService
from app.domain.protocols.services.course import CourseService as CourseServiceProtocol

from app.domain.protocols.services.client import ClientService as ClientServiceProtocol
from app.domain.services.client import ClientService
from app.domain.models.client import ClientCreate, ClientToCourseCreate

from fastapi_lti1p3 import enforce_auth, SessionCache
from fastapi_lti1p3.errors import AuthValidationError, SessionExpiredError

from app.utils.permissions import SMEInclusive
from app.utils.anonymization import hash_string_using_sha256

router = APIRouter()

_SETTINGS = get_settings()

BASE_PATH = Path(__file__).parent.resolve()

templates = Jinja2Templates(directory="app/app/templates")

@router.post("/launch")
async def lti_launch(
    request: Request, 
    response: Response,
    session_id: Optional[str] = Form(...),
    storage_target: str = Form(...),
    oidc_auth_domain: str = Form(...),
    course_service: CourseServiceProtocol = Depends(CourseService),
    client_service: ClientServiceProtocol = Depends(ClientService)
):
    try:
        session_data = await enforce_auth(request=request, session_id=session_id)
        session_info = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom")
        session_cache = SessionCache()
        print(f"\n\nsession data: {session_data.model_dump()}\n\n")

    except (AuthValidationError, SessionExpiredError) as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.__class__.__name__,
            message=str(e)
        )
    
    # Checks if the canvas course id is registered or if registration is required.
    try:
        course = await course_service.get_one_course(course_id=session_info.get("course_id"))
        course_is_new = False
        await session_cache.set(cache_id=session_data.session_id, key="course_metadata", value=course.model_dump(), store="session")
    
    except DBError as e:
        if e.type == "NoResultFound":
            course_is_new = True
        else:
            response.status_code = e.status_code
            return ErrorResponse(
                code=e.status_code,
                type=e.type,
                message=str(e)
            )
        
    # Checks if user exists in system adds them if not
    try:
        hashed_id = hash_string_using_sha256(session_info.get('user_id'))
        client = await client_service.get_client(platform_id=hashed_id)

        if client is None:
            client = await client_service.add_client(ClientCreate(platform_id=hashed_id))

    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )
    
    session_data.user_credentials.internal_id = client.id
        
    # Updates user_credentials of the session cache for later reference
    await session_cache.set(cache_id=session_data.session_id, key="user_credentials", value=session_data.user_credentials, store='session')

    # Adds client to course if course is not new, if course is new, client is added to the course after the course is created
    try:
        if not course_is_new:
            await client_service.add_client_to_course(
                junction=ClientToCourseCreate(
                    client_id=client.id, 
                    course_id=course.id, 
                    is_sme=bool(session_data.get_roles() & SMEInclusive())
                    )
                )
            
    except DBError as e:
        if e.type == "UniqueViolation":
            pass

        else:
            response.status_code = e.status_code
            return ErrorResponse(
                code=e.status_code,
                type=e.type,
                message=str(e)
            )
        
    # adds the internal id of the client to the context data sent to the UI, used for filtering elements by ownership
    session_info['aspire_id'] = client.id
    session_storage_key = _SETTINGS.SESSION_ID_STORAGE_KEY
    refresh_token_storage_key = _SETTINGS.REFRESH_TOKEN_STORAGE_KEY

    context_data = {
        **session_info, 
        "storage_target": storage_target, 
        "oidc_auth_domain": oidc_auth_domain, 
        "tool_domain": session_data.tool_domain,
        "course_is_new": course_is_new,
        "session_storage_key": session_storage_key,
        "refresh_token_storage_key": refresh_token_storage_key
        }

    html_template = "index.html"

    if _SETTINGS.ENV == "LOCAL":
        html_template = "simulateLTILaunch.html"

    if storage_target == "cookie":
        response = templates.TemplateResponse(
            html_template, 
            context={
                "request": request, 
                "data": context_data, 
                "session_params": {}
                }
            )
        
        response.set_cookie(
            key=session_storage_key, 
            value=session_id, 
            samesite="strict", 
            httponly=True
            )
        
        response.set_cookie(
            key=refresh_token_storage_key,
            value=session_data.refresh_token,
            samesite="strict",
            httponly=True,
            )
    
    else:
        response = templates.TemplateResponse(
            html_template, 
            context={
                "request": request, 
                "data": context_data, 
                "session_params": {
                    "session_id": session_id,
                    "session_expiration": (int((session_data.created_at + timedelta(seconds=session_data.session_expiration)).timestamp()) * 1000),
                    "refresh_token": session_data.refresh_token,
                    }
                }
            )
    
    return response





