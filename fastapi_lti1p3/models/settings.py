from pydantic import BaseModel, Field
from typing import Optional, List, Type
from fastapi_lti1p3.models.cache_models import Session

class ToolConfigSettings(BaseModel):
    """
    Tool specific config settings, these settings are static meaning they should apply regardless of the LMS platform launching the tool.

    :param str or 'fastapi_lti1p3/templates/auth_frames' AUTH_FRAME_REPO: 
    The repository containing the HTML template for use during the OIDC auth response redirect.

    :param str or 'fastapi_lti1p3/templates/dev_launch_frames' DEV_FRAME_REPO: 
    The repository containing the HTML templates for use during development to simulate OIDC launch. ENV must be set to 'LOCAL' for the associated routes to be enabled.

    :param str or 'fastapi_lti1p3/templates/registration_frames' REGISTRATION_FRAME_REPO:
    The repository containing the HTML templates for use during dynamic registration.

    :param str or 'simpleLaunch.html' AUTH_FRAME_TEMPLATE: 
    The HTML template for use for the OIDC auth response redirect. Default template performs a simple form post to the target_link_uri with the session_id, storage_target, and oidc_auth_domain.

    :param str or 'registration_form.html' DYNAMIC_REGISTRATION_TEMPLATE: 
    The HTML template for use for displaying the developer key dynamic registration form.

    :param str or '/oidc/init' OIDC_INITIATION_URL: 
    The domain omitted route handling the 3rd-party OIDC initiation request.

    :param str or '/oidc/response' OIDC_AUTH_REDIRECT_URI: 
    The domain omitted route handling validation of the platform auth response and subsequent redirect to the tools target_link_uri.

    :param str or '/public_jwk' TOOL_JWK_URL:
    The domain omitted route serving the tools public JWK
    
    :param Type[Session] or Session SESSION_CLASS:
    The Pydantic Model stored in and returned by the session_cache, can be overridden to allow for additional fields to be stored in the cache. **WARNING** Additional fields must either be Optional or have a default value.

    :param str TOOL_DOMAIN_NAME:
    The domain name of the tool.

    :param str ENV:
    The current tool environment, set = 'LOCAL' to enable default dev launch flow.

    :param bytes or None LTI_PUBLIC_KEY:
    **WARNING DO NOT SET** Public and Private keys generated on app startup.

    :param bytes or None LTI_PRIVATE_KEY:
    **WARNING DO NOT SET** Public and Private keys generated on app startup.

    """
    application_type: str = "web"
    grant_types: List[str] = ["client_credentials", "implicit"]
    initiate_login_uri: str = "/oidc/init"
    auth_redirect_uri: str = "/oidc/response"
    redirect_uris: List[str] = ["/oidc/response", "/launch"]
    jwk_uri: str = "/public_jwk"
    logo_uri: Optional[str] = None
    icon_uri: Optional[str] = None
    token_endpoint_auth_method: str = "private_key_jwt"
    contacts: Optional[List[str]] = None
    client_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    client_name: str
    # scope: str = ""

    default_domain: Optional[str] = Field(alias="domain", default=None)
    secondary_domains: Optional[List[str]] = None
    secondary_targets: Optional[List[str]] = None
    description: Optional[str] = None

    AUTH_FRAME_REPO: str = "fastapi_lti1p3/templates/auth_frames"
    DEV_FRAME_REPO: str = "fastapi_lti1p3/templates/dev_launch_frames"
    REGISTRATION_FRAME_REPO: str = "fastapi_lti1p3/templates/registration_frames"
    AUTH_FRAME_TEMPLATE: str = "simpleLaunch.html"
    DYNAMIC_REGISTRATION_TEMPLATE: str = "registration_form.html"

    SESSION_CLASS: Type[Session] = Session
    SESSION_EXPIRATION: int = 3600 # Duration until session experiation starting from creation time, in seconds
    SESSION_ID_STORAGE_KEY: str = "lti-session-id"
    REFRESH_TOKEN_STORAGE_KEY: str = "lti-refresh-token"
    ENV: str
    LTI_PUBLIC_KEY: Optional[bytes] = None
    LTI_PRIVATE_KEY: Optional[bytes] = Field(default=None, exclude=True)

    class Config:
        populate_by_name=True


class PlatformConfigSettings(BaseModel):
    """
    LMS platform specific config settings, 
    these settings can either be static if the tool is only launched from one platform, 
    or dynamic if a function is supplied to init_adapted_config that accepts a client_id and returns an instance of PlatformConfigSettings.

    :param str OIDC_AUTH_REQ_URL:
    The platforms OIDC authentication request url.

    :param str OIDC_TARGET_LINK_URI:
    The domain omitted url of the tools launch endpoint.

    :param str OAUTH_TOKEN_GET:
    The platforms OAuth access token GET endpoint.

    :param str OAUTH_TOKEN_POST:
    The platforms OAuth access token POST endpoint.

    :param str PLATFORM_JWK_URL:
    The platforms public JWK URL.

    :param str PLATFORM_ISS:
    The ISS of the LMS platform.

    <hr/>
    ========================================
    Dynamic Platform Config Settings Example:
    ========================================

```python

    from fastapi_lti1p3 import PlatformConfigSettings ToolConfigSettings, init_adapter_config
    from irrelevant_to_example import tool_config
    from fake_db_engine import db

    #Must be async function that accepts a client_id as a string
    async def get_platform_settings(client_id:str) -> PlatformConfigSettings:
        statement = "SELECT ... WHERE client_id == %(client_id)s"
        result = db.execute(statement)
        #process the result however you want, im sure you can work it out.
        ...
        # Function must return an instance of PlatformConfigSettings
        return PlatformConfigSettings(**result)

    
    init_adapter_config(tool_settings=tool_config, platform_settings=get_platform_settings)

```
    """
    platform_auth_req_uri: str
    target_link_uri: str
    platform_access_token_get:str
    platform_access_token_post:str
    jwk_uri: str
    platform_iss: str
    domain: str

    deployment_id: Optional[str] = None
    DEVELOPER_KEY_SCOPES: Optional[List[str]] = None

