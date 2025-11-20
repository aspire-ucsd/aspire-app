from pydantic import BaseModel, Field as PydanticField
from typing import Optional, Literal, Union
from datetime import datetime, UTC, timedelta

class UserCredentials(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[str] = None
    token_type: Optional[str] = None
    internal_id: Optional[Union[int, str]] = None
    platform_id: Optional[Union[int, str]] = None
    user_vars: dict = {}

class Session(BaseModel):
    #Primary Key
    session_id: str
    session_expiration: int = None

    refresh_token: str

    id_token: dict
    csrf_token: str
    user_credentials: UserCredentials = UserCredentials()
    client_id: Optional[str] = None
    tool_domain: Optional[str] = None
    created_at: datetime = PydanticField(default_factory=lambda:datetime.now(UTC))

    def __eq__(self, other):
        if isinstance(other, Session):
            return self.session_id == other.session_id
        if isinstance(other, str):
            return self.session_id == other
        return NotImplemented
    
    def __hash__(self):
        return hash(self.session_id)

    def update(self, **kwargs):
        for field, value in kwargs.items():
            try:
                setattr(self, field, value)
            except ValueError:
                pass

        return self

    def __str__(self) -> str:
        return self.session_id
    

    def get_roles(self):
        """
        Called within enforce_auth for role based authorization.
        Exception handling deffered to implementer
        """
        raise NotImplemented
    
    def set_roles(self) -> None:
        """
        Called at the creation of a session after the LTI launch is validated, roles are used by the enforce_auth function.
        Exception handling deffered to implementer
        """
        raise NotImplemented
    
    def set_platform_id(self) -> Union[int, str, None]:
        """
        Called at the creation of a session after the LTI launch is validated, value returned is added to the user_credentials.platform_id field.
        Requires implementation due to variance in source locations. 
        
        Exception handling deffered to implementer
        """
        raise NotImplemented


class Nonce(BaseModel):
    #Primary Key
    nonce: str
    target_link_uri: str
    client_id: str
    state: str
    storage_target: Optional[str] = "cookie"

    def __eq__(self, other):
        if isinstance(other, Nonce):
            return self.nonce == other.nonce
        if isinstance(other, str):
            return self.nonce == other
        return NotImplemented
    
    def __hash__(self):
        return hash(self.nonce)
    
    def update(self, **kwargs):
        for field, value in kwargs.items():
            try:
                setattr(self, field, value)
            except ValueError:
                pass
            
        return self
    
    def __str__(self) -> str:
        return self.nonce


    