from pydantic import BaseModel, validator, root_validator, Field, validator
from typing import Optional, Literal, List, Union


class DefaultMessageSchema(BaseModel):
    type: Literal["LtiResourceLinkRequest", "LtiDeepLinkingRequest"]
    target_link_uri: Optional[str]
    label: Optional[str]
    icon_uri: Optional[str]
    custom_parameters: Optional[dict]
    placements: Optional[List[str]]
    roles: Optional[List[str]]


class CanvasMessageSchema(DefaultMessageSchema):
    default_enabled: bool = Field(alias="https://canvas.instructure.com/lti/course_navigation/default_enabled", default=True)
    visibility: Optional[Literal["admins", "members", "public"]] = Field(alias="https://canvas.instructure.com/lti/visibility")


class DefaultToolConfiguration(BaseModel):
    domain: str
    secondary_domains: Optional[List[str]]
    target_link_uri: str
    custom_parameters: dict = {}
    description: Optional[str]

    messages: List[Union[CanvasMessageSchema, DefaultMessageSchema, None]] = []
    claims: List[Union[str, None]] = []

    deployment_id: Optional[str]

    @validator("target_link_uri")
    def target_include_domain(cls, v, values):
        if values["domain"] not in v:
            return f"{values['domain']}{v}"
        return v
    
    class Config:
        populate_by_name=True



class CanvasToolConfiguration(DefaultToolConfiguration):
    privacy_level: Optional[Literal["public", "name_only", "email_only", "anonymous"]] = Field(alias="https://canvas.instructure.com/lti/privacy_level")
    tool_id: Optional[str] = Field(alias="https://canvas.instructure.com/lti/tool_id")



class RegistrationSchema(BaseModel):
    domain: str = Field(exclude=True)
    application_type: str = "web"
    grant_types: List[str] = ["client_credentials", "implicit"]
    initiate_login_uri: str
    redirect_uris: List[str]
    response_types: List[str] = ["id_token"]
    client_name: str
    jwk_uri: str
    logo_uri: Optional[str]
    token_endpoint_auth_method: str = "private_key_jwt"
    contacts: Optional[List[str]]
    client_uri: Optional[str]
    tos_uri: Optional[str]
    policy_uri: Optional[str]

    scope: str = ""

    lti_tool_configuration: Union[DefaultToolConfiguration, CanvasToolConfiguration] = Field(alias="https://purl.imsglobal.org/spec/lti-tool-configuration")

    @validator("jwk_uri")
    def jwk_include_domain(cls, v, values):
        if values["domain"] not in v:
            return f"{values['domain']}{v}"
        return v
    
    @validator("initiate_login_uri")
    def login_include_domain(cls, v, values):
        if values["domain"] not in v:
            return f"{values['domain']}{v}"
        return v
    
    @validator("redirect_uris")
    def redirect_include_domain(cls, v, values):
        for index, val in enumerate(v):
            if values["domain"] not in val:
                v[index] = f"{values['domain']}{val}"
        return v
    
    class Config:
        populate_by_name=True