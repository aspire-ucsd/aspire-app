import requests

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import jwt

from .models.settings import ToolConfigSettings

def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

async def get_developer_key_json(tool_public_jwk_url: str, _settings: ToolConfigSettings):
    dev_key = {
        "title": _settings.WEB_APP_TITLE,
        "description": _settings.WEB_APP_DESCRIPTION,
        "oidc_initiation_url": _settings.initiate_login_uri,
        "target_link_uri": _settings.OIDC_TARGET_LINK_URI,
        "public_jwk_url": tool_public_jwk_url,
        "extensions": [
            {
                "domain": "ASPIRE-App",
                "tool_id": "dawds32656",
                "platform": "canvas.instructure.com",
                "privacy_level": "public",
                "selection_height": 800,
                "selection_width": 800,
                "placements": [
                {
                    "text": "User Navigation Placement",
                    "placement": "user_navigation",
                    "message_type": "LtiResourceLinkRequest",
                    "target_link_uri": "https://your.target_link_uri/my_dashboard",
                    "canvas_icon_class": "icon-lti",
                    "custom_fields": {
                    "foo": "$Canvas.user.id"
                    }
                }
                ]
            }
        ]
    }
    return dev_key


async def get_platform_public_key(platform_jwk_url: str, settings: ToolConfigSettings):
    # TODO: use async request
    """
    Retrieves the platform public key for id_token signature validation.

    ==============================
    --DISABLED OUTSIDE LOCAL DEV--
    ==============================

    If a session is required during local development while outside of an LMS environment, 
    the OIDC auth flow can be simulated by your application. 
    Since an id_token is required in the auth response step, 
    you will need to generate your own and supply a url to return the appropriate public JWK for signature validation.
    If using the libraries internal JWT and JWK methods, 
    ou will need to set the PlatformConfigSettings.PLATFORM_JWK_URL == 'USE_DEV' and ToolConfigSettings.ENV == 'LOCAL'. 
    This will bypass the HTTP request for a public JWK in favor of the libraries internal Public Key method, 
    allowing for the self generated JWT id_token signature to be validated. 
    """
    if platform_jwk_url == "USE_DEV" and settings.ENV == "LOCAL":
        return await get_tool_public_key(settings=settings)
    else:
        platform_key = requests.get(url=platform_jwk_url).json()
        return platform_key


async def get_tool_public_key(settings: ToolConfigSettings):
    key = load_pem_public_key(settings.LTI_PUBLIC_KEY)
    jwk = jwt.algorithms.RSAAlgorithm.to_jwk(key, as_dict=True)
    jwk["alg"] = "RS256"
    jwk["kid"] = "aksdjhkuahdlkahj-adaldhakihdad46ad432%"
    jwk["use"] = "sig"

    return {
        "keys": [jwk]
        }

