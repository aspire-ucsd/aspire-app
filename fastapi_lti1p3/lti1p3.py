import secrets
import uuid
import jwt
from datetime import datetime, UTC, timedelta

from fastapi import Request
from fastapi.responses import JSONResponse

from urllib.parse import urlencode

from .session_cache import SessionCache, Nonce
from .protocols.lti1p3 import LTI as LTIProtocol
from .config import AdapterConfig

from .auth_response_validator import AuthResponseValidator


class LTI(LTIProtocol):
    def __init__(self, request: Request):
        """
        Contains methods for handling the LTI1.3 launch process with FastAPI and generating/managing persistent client-sessions
        :param request: A FastAPI request object, the content of this request object must be appropriate for method used during the various launch steps
        """
        self._request: Request = request
        self._adapter_config = AdapterConfig()
        self.session_cache = SessionCache()
        self._TOOl_SETTINGS = self._adapter_config.get_tool_settings()
    
    async def create_jwt(self, aud: str, nonce: str, params: dict = {}):
        """
        ==============================
        --DISABLED OUTSIDE LOCAL DEV--
        ==============================
        NOT A FULL OR SECURE IMPLEMENTATION

        Creates a signed JWT, currently used only for simulating the OIDC auth process in a local env.
        """

        if self._TOOl_SETTINGS.ENV != "LOCAL":
            raise NotImplementedError
        
        else:
            payload = {
                "iss": f"{self._TOOl_SETTINGS.default_domain}.com",
                "aud": aud,
                "sub": "c6ceb7cb-8d01-4dfa-8bbb-6425039e638b",
                "exp": (datetime.now(UTC) + timedelta(minutes=10.0)).timestamp(),
                "iat": datetime.now(UTC).timestamp(),
                "nonce": nonce,
                "azp": aud
            }
            payload.update(params)
            encoded_jwt = jwt.encode(payload=payload, key=self._TOOl_SETTINGS.LTI_PRIVATE_KEY, algorithm="RS256", headers={"kid": "aksdjhkuahdlkahj-adaldhakihdad46ad432%"})
            return encoded_jwt


    async def get_session_info(self, session_id):
        session_data = await self.session_cache.get(cache_id=session_id, store="session")
        session_info = session_data.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom")
        return session_info


    async def _create_nonce_session(self, client_id: str, target_link_uri: str, storage_target: str="cookie") -> tuple[Nonce, str]:
        """
        Generates a new nonce value and csrf token, caches them in a new nonce session, then returns the nonce object and csrf token

        :param client_id: The client_id field from the initiated login request, used to validate the request is coming from an accepted origin
        :param target_link_uri: The target_link_uri field from the initiated login request, used to set the final redirect
        """
        nonce = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        #TODO: Might be a risk of the nonce value becoming a duplicate of an existing one due to use of token_urlsafe instead of uuid4, 
        # since I need it to be both a shared secret and an identifier for the cache im not sure of the best approach. 
        # This is probably fine given 32 bit length and regular deletion of entries in the nonce_store after auth completion, if not a different approach is necessary
        await self.session_cache.create_cache(
            value=Nonce(
                nonce=nonce, 
                target_link_uri=target_link_uri, 
                client_id=client_id, 
                state=csrf,
                storage_target=storage_target
            )
        )
        return nonce, csrf


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
        init_token = await self._request.form()

        storage_target = "cookie"
        
        if init_token.get("lti_storage_target"):
            #presence of lti_storage_target key determines where the final session_id is to be stored dependent on 3rd-party cookie support
            storage_target = init_token.get("lti_storage_target")
            
        client_id = init_token.get("client_id")
    
        #Validates client_id if dynamic registration is implemented - Throws ClientIdError
        _platform_settings = await self._adapter_config.get_platform_settings(client_id=client_id)

        target_link_uri = init_token.get("target_link_uri")
        login_hint = init_token.get("login_hint")
        override_params = init_token.get("params")
        nonce, csrf = await self._create_nonce_session(client_id=client_id, target_link_uri=target_link_uri, storage_target=storage_target)

        params = {
            "response_type": "id_token", 
            "response_mode": "form_post",
            "client_id": client_id, 
            "redirect_uri": f"{_platform_settings.domain}{self._TOOl_SETTINGS.auth_redirect_uri}",
            "nonce": nonce,
            "state": csrf,
            "scope": "openid",
            "login_hint": login_hint,
            "prompt": None,
            "params": override_params
            }

        auth_req_url = f"{_platform_settings.platform_auth_req_uri}?{urlencode(params)}"

        return auth_req_url

    
    async def validateResponse(self) -> tuple[str, str, str]:
        """
        Validates the platforms auth response, if no errors are raised, creates a new client-session and returns the uuid of that session and a new csrf token. 

        Used in step 3 of the LTI1.3 launch process: 
        https://www.imsglobal.org/spec/security/v1p0/#step-3-authentication-response
    
        :returns: (session_id, storage_target)
        :rtype: tuple
        :raises TokenValidationError: If the token is invalid, the message attribute contains the cause and the status_code attribute contains the recommended http response status code
        """
        auth_validator = AuthResponseValidator(request=self._request)
        
        validated_token, storage_target = await auth_validator.validate_token()
        session_id = uuid.uuid4().hex
        csrf_token = secrets.token_urlsafe(32)

        platform_config = await self._adapter_config.get_platform_settings(client_id=validated_token["aud"])
        
        #Create new client session
        new_session = self._TOOl_SETTINGS.SESSION_CLASS(
            session_id=session_id, 
            id_token=validated_token, 
            csrf_token=csrf_token, 
            client_id=validated_token['aud'],
            tool_domain=platform_config.domain,
            session_expiration=self._TOOl_SETTINGS.SESSION_EXPIRATION,
            refresh_token=secrets.token_urlsafe(32)
            )
        
        new_session.set_roles()
        new_session.set_platform_id()
        
        await self.session_cache.create_cache(new_session)

        return session_id, storage_target, validated_token
    
    async def refresh_session(self) -> JSONResponse:
        old_session_key = self._TOOl_SETTINGS.SESSION_ID_STORAGE_KEY
        refresh_token_key =self._TOOl_SETTINGS.REFRESH_TOKEN_STORAGE_KEY
        storage_target = 'cookie'
        try:
            refresh_data = self._request.cookies

            old_session_id = refresh_data[old_session_key]
            refresh_token = refresh_data[refresh_token_key]

        except KeyError:
            try:
                refresh_data = self._request.headers

                old_session_id = refresh_data[old_session_key]
                refresh_token = refresh_data[refresh_token_key]
                storage_target="lti.put_data"

            except Exception as e:
                raise ValueError("Missing required fields: Session ID and Refresh Token not found in cookies or headers")
            
        new_session = await self.session_cache.refresh_session(old_cache_id=old_session_id, refresh_token=refresh_token, session_expiration=self._TOOl_SETTINGS.SESSION_EXPIRATION)

        if storage_target == "cookie":
            response = JSONResponse(
                content={
                    "msg": 'Session successfully refreshed',
                    "storage_target": storage_target,
                    }
                )
            response.set_cookie(
                key=old_session_key, 
                value=new_session.session_id, 
                samesite="strict", 
                httponly=True,
                expires=int((new_session.created_at + timedelta(seconds=new_session.session_expiration)).timestamp()) * 1000
                )
        
            response.set_cookie(
                key=refresh_token_key,
                value=new_session.refresh_token,
                samesite="strict",
                httponly=True,
                )
        else:
            response = JSONResponse(
                content={
                    "msg": 'Session successfully refreshed',
                    "storage_target": storage_target,
                    "new_session_id": new_session.session_id, 
                    "refresh_token": new_session.refresh_token,
                    "session_expiration": int((new_session.created_at + timedelta(seconds=new_session.session_expiration)).timestamp()) * 1000
                    }
                )

        return response
    

    # async def get_access_token(
    #     self, 
    #     session_id:str,
    #     params: OAuthGet,
    #     store:bool=True
    # ):
    #     """
    #     Retrieves an access token for use on behalf of a logged in user, token stored in session storage
    #     """
    #     async with httpx.AsyncClient() as client:
    #         grant_post_url = self._settings.OAUTH_CLIENT_GRANT_POST
    #         response = await client.post(grant_post_url, params=params.dict(exclude_none=True))

    #         response_dict = response.json()
    #         client_credentials = UserCredentials(
    #             access_token=response_dict["access_token"],
    #             refresh_token=response_dict["refresh_token"],
    #             expires_in=response_dict["expires_in"],
    #             token_type=response_dict["token_type"],
    #             user_id=response_dict["user"]["id"],
    #             name=response_dict["user"]["name"],
    #             global_id=response_dict["user"]["global_id"]
                
    #             )
    #         self.session_cache.set(cache_id=session_id, key="client_credentials", value=client_credentials, store="session")