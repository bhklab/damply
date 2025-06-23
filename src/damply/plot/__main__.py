import click
from rich import Console
from damply.logging_config import logger

cols = [
    'path',
    'parent',
    'name',
    'size',
    'size_gb',
    'file_count',
    'owner',
    'group',
    'full_name',
    'permissions',
    'last_modified',
    'last_changed',
    'readme_path',
    'meta.OWNER',
    'meta.DESC',
    'meta.EMAIL',
    'meta.DATE',
    'file_types',
]