from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message="support for supplying keyword arguments to pathlib.PurePath is deprecated")

class Directory(Path):
    """Represents a directory with additional metadata."""
    size_GB: int

    def __new__(cls, *args, **kwargs) -> Directory:
        _path = Path(args[0]).expanduser().resolve()
        if not _path.is_dir():
            errmsg = f"Directory does not exist: {_path}"
            raise FileNotFoundError(errmsg)
        elif not _path.exists():
            errmsg = f"Directory does not exist: {_path}"
            raise FileNotFoundError(errmsg)
        self = super().__new__(cls, _path)
        self.size_GB = kwargs.get("size_GB", 0)
        return self

    @property
    def last_modification_time(self) -> int:
        """Returns the latest modification time of the directory and its contents."""
        return max(
            (f.stat().st_mtime for f in Path(self).rglob('*') if f.is_file()),
            default=self.stat().st_mtime
        )

    @property
    def last_modification_timestamp(self) -> datetime:
        """Returns the datetime object for the last modification time."""
        return datetime.fromtimestamp(self.last_modification_time)

    @property
    def file_count(self) -> int:
        """Returns the number of files in the directory."""
        return sum(1 for _ in self.rglob('*') if _.is_file())

    @property
    def total_size(self) -> int:
        """Returns the total size of the directory in bytes."""
        return sum(f.stat().st_size for f in self.rglob('*') if f.is_file())

    @property
    def has_subdirectories(self) -> bool:
        """Checks if the directory contains subdirectories."""
        return any(f.is_dir() for f in self.iterdir())

    def __repr__(self) -> str:
        return f"Directory({self.absolute()}, {self.size_GB}GB, Last Modified: {self.last_modification_timestamp})"


@dataclass
class DirectoryList:
    directories: List[Directory]

    @property
    def common_root(self) -> Path:
        dirs = [directory for directory in self.directories]
        common_path = os.path.commonpath(dirs)
        return Path(common_path)

    def __len__(self) -> int:
        return len(self.directories)

    def __getitem__(self, key: int) -> Directory:
        return self.directories[key]

    def __repr__(self):
        fmt_str = ""
        fmt_str += f"CommonPre:{self.common_root}\n"
        for directory in self.directories:
            fmt_str += f"{directory}\n"
        return fmt_str

    def dir_size_dict(self) -> Dict[Path, int]:
        return {
            directory.directory: directory.size_GB for directory in self.directories
        }

if __name__ == "__main__":
    directories = [
        d for d in Path('/cluster/projects/radiomics/Projects').iterdir() if d.is_dir()
    ]
    # print("\n".join([str(d) for d in directories]))
    directories = [Directory(directory, size_GB = 10) for directory in directories]
    directory_list = DirectoryList(directories)
    print(directory_list)


    print(directory_list[0])