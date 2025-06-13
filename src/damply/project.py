import stat
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

import rich.repr
from rich import print
from bytesize import ByteSize

from damply.utils import get_directory_size, count_files


@dataclass
class DirectoryAudit:
	path: Path
	owner: str
	group: str
	full_name: str
	permissions: str
	last_accessed: date
	last_modified: date
	last_changed: date

	# lazy evaluated because expensive
	size: ByteSize | None = field(default=None, init=False)
	file_count: int | None = field(default=None, init=False)

	last_computed: str | None = field(default=None, init=False, repr=False)

	@classmethod
	def from_path(cls, path: Path) -> 'DirectoryAudit':
		# resolve ~ and expand environment variables and canonicalize the path
		path = path.expanduser().resolve()
		if not path.exists():
			msg = f'The path {path} does not exist.'
			raise FileNotFoundError(msg)

		stats = path.stat()

		try:
			from grp import getgrgid
			from pwd import getpwuid

			pwuid_name = getpwuid(stats.st_uid).pw_name
			pwuid_gecos = getpwuid(stats.st_uid).pw_gecos
			group_name = getgrgid(stats.st_gid).gr_name
		except ImportError:
			pwuid_name = 'Unknown'
			pwuid_gecos = 'Unknown'
			group_name = 'Unknown'
		except KeyError:
			pwuid_name = 'Unknown'
			pwuid_gecos = 'Unknown'
			group_name = 'Unknown'

		toronto_tz = ZoneInfo('America/Toronto')
		return DirectoryAudit(
			path=path,
			owner=pwuid_name,
			group=group_name,
			full_name=pwuid_gecos,
			permissions=stat.filemode(stats.st_mode),
			last_accessed=datetime.fromtimestamp(stats.st_atime, tz=toronto_tz).date(),
			last_modified=datetime.fromtimestamp(stats.st_mtime, tz=toronto_tz).date(),
			last_changed=datetime.fromtimestamp(stats.st_ctime, tz=toronto_tz).date(),
		)

	def compute_details(self, show_progress: bool = True) -> None:
		self.size = self.compute_size(show_progress=show_progress)
		self.file_count = self.compute_file_count(show_progress=show_progress)
		self.last_computed = datetime.now(ZoneInfo('America/Toronto')).strftime(
			'%Y-%m-%d %H:%M:%S'
		)

	def compute_file_count(self, show_progress: bool = True) -> int:
		if self.file_count is None:
			self.file_count = count_files(
				directory=self.path, show_progress=show_progress
			)
		return self.file_count

	def compute_size(self, show_progress: bool = True) -> ByteSize:
		if self.size is None:
			self.size = get_directory_size(
				directory=self.path, show_progress=show_progress
			)
		return self.size

	def __rich_repr__(self) -> rich.repr.Result:
		yield 'path', self.path.absolute()
		yield 'owner', self.owner
		yield 'group', self.group
		yield 'full_name', self.full_name
		yield 'permissions', self.permissions
		yield 'last_accessed', self.last_accessed
		yield 'last_modified', self.last_modified
		yield 'last_changed', self.last_changed
		yield 'size', self.size if self.size is not None else 'Not computed yet'
		yield (
			'file_count',
			self.file_count if self.file_count is not None else 'Not computed yet',
		)

	def to_dict(self) -> dict:
		return {k: v for k, v in asdict(self).items() if not k.startswith('_')}

	def to_json(self, indent: int = 4) -> str:
		import json

		return json.dumps(self.to_dict(), default=str, indent=indent)


if __name__ == '__main__':
	from rich import print

	audit = DirectoryAudit.from_path(
		Path('/cluster/projects/radiomics/Projects/IterSeg')
	)
	print(audit)

	print('*' * 20)
	print(audit.to_dict())
	print('*' * 20)
	print(audit.to_json())

	print('*' * 20)
	audit.compute_size()
	print(f'Size: {audit.size:.2f:GB}')

	print('*' * 20)
	print(audit.to_dict())
