"""Custom exceptions for the dmpdirs package."""

class DirectoryNotFoundError(Exception):
    """Exception raised when a required project directory does not exist."""
    
    def __init__(self, directory_name, directory_path):
        self.directory_name = directory_name
        self.directory_path = directory_path
        message = f"Project directory '{directory_name}' does not exist at '{directory_path}'"
        super().__init__(message)
