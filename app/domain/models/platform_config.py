from typing import Optional, List, Union

from sqlmodel import Field, SQLModel, Column, ARRAY, String

class PlatformConfig(SQLModel, table=True):
    __tablename__ = "platform_config"
    CLIENT_ID: Optional[str] = Field(default=None, primary_key=True)
    # DEVELOPER_KEY_SCOPES: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String())))
    platform_auth_req_uri: str
    target_link_uri: str
    platform_access_token_get:str
    platform_access_token_post:str
    jwk_uri: str
    platform_iss: str
    deployment_id: Optional[str] = None
    domain: str
    
class PlatformConfigRead(PlatformConfig):
    pass

class PlatformConfigCreate(PlatformConfig):
    pass