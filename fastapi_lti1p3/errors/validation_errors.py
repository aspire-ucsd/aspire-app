from .base_error import BaseError

class SessionExpiredError(Exception):
    """Raised when accessing expired sessions."""
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return self.message

class NonceValidationError(BaseError):
    pass


class StateValidationError(BaseError):
    pass


class TokenValidationError(BaseError):
    pass

class ConfigValidationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self):
        return self.message

    
class AuthValidationError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
            self.status_code = status_code
            self.message = message

    def __str__(self):
        return self.message
    
