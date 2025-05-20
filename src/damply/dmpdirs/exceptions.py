"""Custom exceptions for the dmpdirs package."""


class DirectoryNameNotFoundError(Exception):
	"""Exception raised when a required project directory name is not found in the config."""

	def __init__(self, directory_name: str, directory_path: str) -> None:
		self.directory_name = directory_name
		message = (
			f"Project directory name '{directory_name}' not found in configuration"
			f" or does not exist at '{directory_path}'"
		)
		super().__init__(message)
