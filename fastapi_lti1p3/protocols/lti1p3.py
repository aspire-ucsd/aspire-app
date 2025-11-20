from typing import Protocol
from ..session_cache import Nonce
from fastapi.responses import JSONResponse

class LTI(Protocol):

    async def create_jwt(self, aud: str, nonce: str, params: dict = {}):
        """
        ==============================
        --DISABLED OUTSIDE LOCAL DEV--
        ==============================
        NOT A FULL OR SECURE IMPLEMENTATION

        Creates a signed JWT, currently used only for simulating the OIDC auth process in a local env.
        """
        ...


    async def get_session_info(self, session_id):
        ...


    async def _create_nonce_session(self, client_id: str, target_link_uri: str, storage_target: str="cookie") -> tuple[Nonce, str]:
        """
        Generates a new nonce value and csrf token, caches them in a new nonce session, then returns the nonce object and csrf token

        :param client_id: The client_id field from the initiated login request, used to validate the request is coming from an accepted origin
        :param target_link_uri: The target_link_uri field from the initiated login request, used to set the final redirect
        """
        ...


    async def create_auth_response(self) -> str:
        """
        Used in steps 1 & 2 of the LTI1.3 launch process: 
        https://www.imsglobal.org/spec/security/v1p0/#step-1-third-party-initiated-login
        https://www.imsglobal.org/spec/security/v1p0/#step-2-authentication-request
        
        Takes the iss, login_hint, and target_link from the Third-party initiated login response from the lms platform,
        generates a nonce value and csrf token, stores them in a temporary nonce session,
        then packages an Authentication request with the appropriate query params, returning a url for the redirect.

        :returns: A url string with attached query params for the auth request redirect
        :rtype: str
        """
        ...

    
    async def validateResponse(self) -> tuple[str, str, str]:
        """
        Validates the platforms auth response, if no errors are raised, creates a new client-session and returns the uuid of that session and a new csrf token. 

        Used in step 3 of the LTI1.3 launch process: 
        https://www.imsglobal.org/spec/security/v1p0/#step-3-authentication-response
    
        :returns: (session_id, storage_target)
        :rtype: tuple
        :raises TokenValidationError: If the token is invalid, the message attribute contains the cause and the status_code attribute contains the recommended http response status code
        """
        ...
    
    async def refresh_session(self) -> JSONResponse:
        ...