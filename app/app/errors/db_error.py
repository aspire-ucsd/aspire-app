class DBError(Exception):
    def __init__(self, origin: str, type: str, status_code: int, message: str) -> None:
        self.origin = origin
        self.status_code = status_code
        self.type = type
        self.message = message

    def __str__(self):
        return f"Error: {self.message}"