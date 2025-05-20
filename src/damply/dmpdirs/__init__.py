"""dmpdirs: Standardized access to project directories in data science workflows.

This package provides convenient access to common directories in data science projects,
supporting two standard directory structures and handling path resolution.

Project root is determined in the following order:
1. From DMP_PROJECT_ROOT environment variable (if set)
2. From PIXI_PROJECT_ROOT environment variable (if set)
3. Current working directory as fallback

Structure 1: Flat Layout (legacy DMP Structure)
```console
project_root/
├── rawdata/        # Raw input data
├── procdata/       # Processed/intermediate data
├── results/        # Analysis outputs and figures
├── workflow/       # Code organization
│   ├── notebooks/  # Jupyter notebooks
│   └── scripts/    # Analysis scripts
├── logs/           # Log files
├── config/         # Configuration files
└── metadata/       # Dataset descriptions
```

Structure 2: Nested Layout (newer DMP Structure)
```console
project_root/
├── config/         # Configuration files
├── data/           # All data in one parent directory
│   ├── procdata/   # Processed/intermediate data
│   ├── rawdata/    # Raw input data
│   └── results/    # Analysis outputs
├── logs/           # Log files
├── metadata/       # Dataset descriptions
└── workflow/       # Code organization
    ├── notebooks/  # Jupyter notebooks
    └── scripts/    # Analysis scripts
```

Usage:
    from dmpdirs import dirs

    # Access paths as Path objects
    data_file = dirs.RAWDATA / "dataset.csv"

    # Print absolute paths
    print(dirs.RAWDATA)  # e.g., /Users/username/projects/my_project/rawdata

    # Access directory structure
    print(dirs.STRUCTURE)  # "flat" or "nested"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Dict

from .exceptions import DirectoryNotFoundError


def get_project_root() -> Path:
	"""Get the project root directory."""
	# Check if the environment variable is set
	if project_root := os.getenv('DMP_PROJECT_ROOT') or (
		project_root := os.getenv('PIXI_PROJECT_ROOT')
	):
		return Path(project_root).resolve()

	# If not, use the current working directory
	return Path.cwd().resolve()


def detect_directory_structure(root_path: Path) -> str:
	"""Detect the directory structure type.

	Args:
	    root_path: Project root path

	Returns:
	    str: "flat" or "nested" indicating the detected structure
	"""
	# Check if "data" directory exists and contains at least one of rawdata/procdata/results
	data_dir = root_path / 'data'
	if data_dir.is_dir() and any(
		(data_dir / subdir).is_dir() for subdir in ['rawdata', 'procdata', 'results']
	):
		return 'nested'
	return 'flat'


class DamplyDirs:
	"""Class that provides computed properties for project directories.

	This class provides computed properties that lazily evaluate directory paths
	and raise appropriate errors if directories don't exist when accessed.

	Usage:
		# Import the pre-instantiated singleton
		from damply.dmpdirs import dirs

		# Access directory paths as Path objects
		rawdata_path = dirs.RAWDATA
		config_file = dirs.CONFIG / "settings.yaml"

		# Get the detected directory structure ("flat" or "nested")
		structure = dirs.STRUCTURE

		# Use dictionary-like access (alternative syntax)
		results_dir = dirs["RESULTS"]

		# Print directory structure representation
		print(dirs)  # Displays a tree-like visualization

	Available directories:
		- PROJECT_ROOT: Root directory of the project
		- RAWDATA: Raw input data directory
		- PROCDATA: Processed/intermediate data directory
		- RESULTS: Analysis outputs directory
		- METADATA: Dataset descriptions directory
		- LOGS: Log files directory
		- CONFIG: Configuration files directory
		- SCRIPTS: Analysis scripts directory
		- NOTEBOOKS: Jupyter notebooks directory

	Attributes:
		STRUCTURE: Returns the detected directory structure ("flat" or "nested").

	Methods:
		__getitem__(key): Access directories using dictionary-like syntax.
		__dir__(): Returns list of available attributes for tab completion.
		__repr__(): Returns a tree-like representation of the directory structure.

	Notes:
		- Directories are resolved lazily when first accessed.
		- DirectoryNotFoundError is raised if a requested directory doesn't exist.
		- The class implements the Singleton pattern; all imports reference the same instance.
	"""

	# Class variable to hold singleton instance
	_instance: ClassVar[DamplyDirs | None] = None

	def __new__(cls) -> DamplyDirs:
		"""Implement singleton pattern."""
		if cls._instance is None:
			cls._instance = super(DamplyDirs, cls).__new__(cls)
			cls._instance._initialized = False
		return cls._instance

	def __init__(self) -> None:
		"""Initialize the DamplyDirs object."""
		# Skip initialization if already initialized
		if getattr(self, '_initialized', False):
			return

		# Initialize core attributes
		self._project_root = get_project_root()
		self._structure = detect_directory_structure(self._project_root)
		self._dir_cache: Dict[str, Path] = {}
		self._initialized = True

	def _get_dir_path(self, dir_name: str) -> Path:
		"""Get the path for a directory based on the project structure.

		Args:
		    dir_name: The name of the directory to get

		Returns:
		    Path object for the requested directory

		Raises:
		    DirectoryNotFoundError: If the directory doesn't exist
		"""
		# Return from cache if available
		if dir_name in self._dir_cache:
			return self._dir_cache[dir_name]

		# Calculate path based on directory name and structure
		if dir_name == 'PROJECT_ROOT':
			path = self._project_root
		elif dir_name in ['RAWDATA', 'PROCDATA', 'RESULTS']:
			# Data directories depend on the structure
			if self._structure == 'nested':
				path = self._project_root / 'data' / dir_name.lower()
			else:
				path = self._project_root / dir_name.lower()
		elif dir_name in ['SCRIPTS', 'NOTEBOOKS']:
			path = self._project_root / 'workflow' / dir_name.lower()
		else:
			# Common directories for both structures
			path = self._project_root / dir_name.lower()

		# Cache the path
		self._dir_cache[dir_name] = path

		# Check if directory exists and raise error if not
		if not path.exists():
			raise DirectoryNotFoundError(dir_name, str(path))

		return path

	def __getattr__(self, name: str) -> Path:
		"""Get attribute for a directory name.

		Args:
		    name: The name of the directory to get

		Returns:
		    Path object for the requested directory

		Raises:
		    AttributeError: If the attribute is not a recognized directory
		    DirectoryNotFoundError: If the directory doesn't exist
		"""
		if name.isupper() and name in [
			'PROJECT_ROOT',
			'RAWDATA',
			'PROCDATA',
			'RESULTS',
			'METADATA',
			'LOGS',
			'CONFIG',
			'SCRIPTS',
			'NOTEBOOKS',
		]:
			return self._get_dir_path(name)
		errmsg = (
			f"'{name}' is not a valid directory name. "
			'Valid names are: PROJECT_ROOT, RAWDATA, PROCDATA, RESULTS, '
			'METADATA, LOGS, CONFIG, SCRIPTS, NOTEBOOKS'
		)
		raise AttributeError(errmsg)

	@property
	def STRUCTURE(self) -> str:  # noqa: N802
		"""Get the detected directory structure."""
		return self._structure

	def __getitem__(self, key: str) -> Path:
		"""Allow dictionary-like access to directories.

		Args:
		    key: The name of the directory to get

		Returns:
		    Path object for the requested directory

		Raises:
		    KeyError: If the key is not a recognized directory
		    DirectoryNotFoundError: If the directory doesn't exist
		"""
		try:
			return getattr(self, key)
		except AttributeError as ae:
			msg = f"'{key}' is not a valid directory name"
			raise KeyError(msg) from ae

	def __dir__(self) -> list[str]:
		"""Return list of available attributes for tab completion."""
		return [
			'PROJECT_ROOT',
			'RAWDATA',
			'PROCDATA',
			'RESULTS',
			'METADATA',
			'LOGS',
			'CONFIG',
			'SCRIPTS',
			'NOTEBOOKS',
			'STRUCTURE',
		]

	def __repr__(self) -> str:
		"""Return a tree-like representation of the directory structure."""
		structure_type = f'Structure: {self._structure.upper()}'
		root_info = f'Project Root: {self._project_root}'

		# Create tree structure
		tree = [f'DamplyDirs<{structure_type}>', root_info]

		for dir_name in sorted(self.__dir__()):
			if dir_name not in ['PROJECT_ROOT', 'STRUCTURE'] and dir_name.isupper():
				try:
					path = getattr(self, dir_name)
					tree.append(
						f'{dir_name:<13}: ├── {path.relative_to(self._project_root)}'
					)
				except DirectoryNotFoundError:
					tree.append(f'{dir_name:<13}: ├── <not found>')

		# Fix the last item to use └── instead of ├──
		if len(tree) > 3:
			tree[-1] = tree[-1].replace('├──', '└──')

		return '\n'.join(tree)


# Create a singleton instance that will be imported by users
dirs = DamplyDirs()
