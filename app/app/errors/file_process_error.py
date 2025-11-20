class FileProcessError(Exception):
    def __init__(self, message, file) -> None:
        self.message = message
        self.file = file
    
    def __str__(self):
        return f"{self.message}\nError occurred at file:{repr(self.file)}"