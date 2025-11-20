from typing import Optional
from pydantic import BaseModel
from ..session_cache import Session

class AuthValidation(BaseModel):
    is_valid: bool
    recommended_http_code: int
    message: str
    session_data: Optional[Session]