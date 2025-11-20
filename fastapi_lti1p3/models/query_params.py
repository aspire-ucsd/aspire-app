from pydantic import BaseModel, validator, root_validator
from typing import Optional, Literal


class OAuthGet(BaseModel):
    grant_type:Literal["authorization_code", "refresh_token", "client_credentials"]="authorization_code"
    client_id: Optional[int]
    client_secret: Optional[str]
    redirect_uri: Optional[str]
    code: Optional[str]
    refresh_token: Optional[str]
    client_assertion_type: Optional[str]
    client_assertion: Optional[str]
    scope: Optional[str]
    replace_tokens: Optional[int]
    
    @root_validator(skip_on_failure=True)
    def validate_field_by_grant(cls, values):
        value = values["grant_type"]
        if value == "authorization_code":
            assert values["client_id"] is not None
            assert values["client_secret"] is not None
            assert values["redirect_uri"] is not None
            assert values["code"] is not None
            assert values["refresh_token"] is None
            assert values["client_assertion_type"] is None
            assert values["client_assertion"] is None
            assert values["scope"] is None

        elif value == "refresh_token":
            assert values["client_id"] is not None
            assert values["client_secret"] is not None
            assert values["redirect_uri"] is not None
            assert values["code"] is None
            assert values["refresh_token"] is not None
            assert values["client_assertion_type"] is None
            assert values["client_assertion"] is None
            assert values["scope"] is None

        elif value == "client_credentials":
            assert values["client_id"] is None
            assert values["client_secret"] is None
            assert values["redirect_uri"] is None
            assert values["code"] is None
            assert values["refresh_token"] is None
            assert values["client_assertion_type"] is not None
            assert values["client_assertion"] is not None
            assert values["scope"] is not None

        return values