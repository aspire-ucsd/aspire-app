import jwt
import json
import requests

from .config import AdapterConfig

from .utils import get_platform_public_key
from .session_cache import SessionCache, Nonce
from .errors.validation_errors import TokenValidationError
from fastapi import Request



class AuthResponseValidator:
    def __init__(self, request: Request) -> None:
        self._settings = AdapterConfig()
        self._session_cache = SessionCache()
        self._request: Request = request

    async def validate_token(self) -> tuple[dict, str]:
        """
        Validates the token as per https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation

        :returns: The decoded and validated id_token in the form of a dictionary and the storage target
        :raises TokenValidationError: When any validation step fails. the message attribute contains the cause and the status_code attribute contains the recommended http response status code
        """

        # Step-1: Validate nonce and state, we do this first to ensure nonce_session is deleted if nonce is valid regardless of other possible exceptions 
        request_form = await self._request.form()
        token = request_form.get("id_token")

        unevaluated_claims = jwt.decode(token, options={"verify_signature": False})
        nonce = await self._validate_state_and_nonce(claims=unevaluated_claims, request_form=request_form)
        
        # Step-2: Get public key from platform for final decoding and JWT signature validation
        #TODO Add error handling to public key retrieval steps

        _platform_settings = await self._settings.get_platform_settings(client_id=nonce.client_id)
        _tool_settings = self._settings.get_tool_settings()

        platform_public_key = await get_platform_public_key(
            platform_jwk_url=_platform_settings.jwk_uri, 
            settings=_tool_settings
            )

        public_keys = {}

        for jwk in platform_public_key['keys']:
            kid = jwk['kid']
            public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        claims = jwt.get_unverified_header(token)

        kid = claims.get("kid")
        key = public_keys[kid]


        #Step-3 Validate token signature and other misc checks described here: https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation
        try:
            #TODO: Insert actual registered audiences automatically
            payload = jwt.decode(token, key=key, algorithms=['RS256'], audience=[nonce.client_id])

        except jwt.exceptions.InvalidSignatureError as e:
            raise TokenValidationError(message="Invalid Signature - Login from unregistered platforms is forbidden", status_code=401) from e

        except jwt.exceptions.ExpiredSignatureError as e:
            raise TokenValidationError(message="Token Expired", status_code=401) from e

        except jwt.exceptions.InvalidAudienceError as e:
            raise TokenValidationError(message="Invalid Audience Claim", status_code=401) from e
        
        except Exception as e:
            raise TokenValidationError(message="Failed to Validate Token", status_code=400) from e

        return payload, nonce.storage_target


    async def _validate_state_and_nonce(self, claims: dict, request_form) -> Nonce:
        """
        Validates the state and nonce values of the token, the temporary nonce session is automatically deleted upon successful retrieval
        :param claims: The decoded claims of the id_token
        """
        jwt_nonce = claims.get("nonce")
        jwt_state = request_form.get("state")
        try:
            #Validate Nonce exists and matches value stored in cache
            assert jwt_nonce is not None, "Nonce value missing from claims"
            # A successful self._session_cache.get on the nonce data store automatically confirms the validity of the nonce and deletes it in order to enforce single use requirement.
            nonce_session = await self._session_cache.get(cache_id=jwt_nonce, store="nonce")
            assert nonce_session is not None, "Invalid nonce claim"

            #Validate State exists and matches value stored in cache
            assert jwt_state is not None, "State value missing from response"
            assert nonce_session.state == jwt_state, "State value invalid"
            return nonce_session
        
        except AssertionError as e:
            raise TokenValidationError(message=str(e), status_code=401) from e


