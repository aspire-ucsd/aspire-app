class ValidationError(Exception):
    def __init__(self, origin: str, status_code: int, message: str) -> None:
        self.origin = origin
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"Error: {self.message}"