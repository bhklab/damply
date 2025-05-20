import os
import platform
from pathlib import Path


def get_file_owner_full_name(file_path: Path):
	try:
		if platform.system() == 'Windows':
			msg = 'Platform not supported for retrieving user info using pwd module.'
			raise NotImplementedError(msg)

		from pwd import getpwuid

		# Get the file's status
		file_stat = os.stat(file_path)

		# Get the user ID of the file owner
		uid = file_stat.st_uid

		# Get the user information based on the user ID
		user_info = getpwuid(uid)

		# Return the full name of the user
		return user_info.pw_gecos

	except ImportError:
		return file_path.owner()
	except NotImplementedError:
		return 'Retrieving user info is not supported on Windows.'
	except Exception as e:
		return str(e)
