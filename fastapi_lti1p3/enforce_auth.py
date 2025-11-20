from .session_cache import SessionCache, Session
from .errors.validation_errors import AuthValidationError
from .config import AdapterConfig

from fastapi import Request

from typing import Set, Optional, List, Protocol, Union, Any, Tuple

class AccessValidatorProtocol(Protocol):
    def __call__(self, session_data: Optional[Session] = None) -> Union[bool, Any]:
        ...

async def enforce_auth(
        request: Request,
        session_id: Optional[str]=None, 
        accepted_roles: Optional[Set[str]]=None,
    ) -> Union[Tuple[Session, dict], Session]:
    """
    Searches for a session_id in the cookies, headers, or session_id argument, 
    if one exists, it matches a session stored in the SessionCache, 
    and if the user assigned to that session contains any of the accepted roles, 
    returns the Session object of the client.

    Expired sessions are automatically rejected.

    :param request: REQUIRED - The request object of the protected endpoint. Must contain either a cookie or a header containing a valid session_id **EXCEPT** if overridden with the session_id arg.

    :param session_id: OPTIONAL - The id of the client session as generated and stored during the lti launch process, provided in cases where an http request object is unavailable or does not contain the session_id.

    :param accepted_roles: OPTIONAL - A set of strings exactly matching at least one of the required user roles originating from the LMS platform, or None if all roles are acceptable.


    :returns Session: returned only if validation checks pass

    :raises AuthValidationError: If no session is found or session does not contain any of the accepted roles

    <hr/>

    =================
    Expose Headers
    =================
    
    In cases where cookies are blocked by 3rd party cookie policies, 
    enforce_auth is equipped to search for the the session_id within a custom header specified by the 'SESSION_ID_STORAGE_KEY' config variable. 
    In order to allow custom headers to attach to a FastAPI Request object, the specific header must be exposed using the built-in CORS Middleware.
    
    **below is an example of how to do this:**

```python

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI()
    # Add your custom headers to expose_header's list of strings
    app.add_middleware(CORSMiddleware, expose_headers=["x-session-cookie"])

```
    <br/>
    <hr/>

    =================
    Modify Role Check
    =================

    Roles are checked by first evoking the `Session.get_roles()` method, 
    by default this expects roles to exist on the id_token at the "https://purl.imsglobal.org/spec/lti/claim/custom" key as a comma separated string,
    then the result is checked against the conditional `if accepted_roles and not client_roles & accepted_roles:` 
    to determine either if all roles are acceptable or if roles have been specified and the result of `Session.get_roles()` is a subset/superset of the specified roles.

    Because Sessions can be overridden and/or the location where roles are stored may vary it is possible to modify the `Session.get_roles()` method at adapter configuration.

    **Here is an example override:**

```python
    from fastapi_lti1p3 import Session, ToolConfigSettings, init_adapter_config
    from irrelevant_to_example import platform_config
    from typing import List, Optional, Set
    # New model must extend 'Session'
    class ModifiedSession(Session):
        # Example adds an additional 'role' field to the Session class, the value will not be automatically added by the library on session creation,
        # therefore it must be set as Optional and/or with a default value, and added by the developer at a later stage.
        roles: Optional[List[str]]
        # Overrides the default get_roles() method
        def get_roles(self) -> Set[str]:
            # Must return a set of strings
            return set(self.roles)

    # Add new SESSION_CLASS to ToolConfigSettings and initialize.
    tool_config = ToolConfigSettings(**extra_tool_config, SESSION_CLASS=ModifiedSession)
    init_adapter_config(tool_settings=tool_config, platform_settings=platform_config)
```

    """
    
    tool_settings = AdapterConfig().get_tool_settings()
    session_storage_key = tool_settings.SESSION_ID_STORAGE_KEY

    if session_id:
        pass
    
    elif request.cookies.get(session_storage_key):
        session_id = request.cookies.get(session_storage_key)

    elif request.headers.get(session_storage_key):
        session_id = request.headers.get(session_storage_key)

    else:
        raise AuthValidationError(
            status_code=403, 
            message=f"session_id not found - session_id must be supplied in one of the following locations:\n1) In a cookie with a key == {session_storage_key}\n2) In the headers with a key == {session_storage_key}\n3) Supplied directly in the session_id argument"
            )
    try:
        cache = SessionCache()
        session_data = await cache.get(cache_id=session_id, store="session")
    
    except AttributeError as e:
        raise AuthValidationError(status_code=401, message="Access Denied: Authentication Required") from e

    # No session found
    if not session_data:
        raise AuthValidationError(status_code=401, message="Access Denied: Authentication Required")
    
    # accepted_roles not none and Insufficient permissions
    if accepted_roles and not session_data.get_roles() & accepted_roles:
        raise AuthValidationError(status_code=403, message="Access Denied: Insufficient Permissions")

    return session_data

    
