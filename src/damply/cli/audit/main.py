
import datetime
import sys
from pathlib import Path
import json
import click
import traceback

from .utils import (
    InvalidProjectGroupError,
    OutsideProjectPathError,
    get_parents_path,
    get_project_group,
)
from damply.project import DirectoryAudit
from damply import __version__ as damply_version
from damply.logging_config import logger

@click.option(
    '--force-compute-details',
    '-f',
    'compute_details',
    help='Force the computation of details for the directory and subdirectories regardless of cache.',
    is_flag=True,
    default=False,
    show_default=True,
)
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.command("audit")
def audit(directory: Path, compute_details: bool) -> None:
    """Audit all subdirectories and aggregate damply output into a single JSON.
    
    Unlike the 'damply proejct' command, this will by default, try to compute
    details, using cache if it exists. If you want to force the computation
    of details for the directory and subdirectories, use the --force-compute-details
    flag. This will ignore any cached results and recompute everything.

    """

    # resolve the directory to scan
    directory = directory.expanduser().resolve().absolute()

    logger.info(f"Starting audit for directory: {directory}")

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
    date = now.strftime("%Y-%m-%d")

    try:
        project_group = get_project_group(directory)
        relative_path = get_parents_path(project_group, directory)
    except (InvalidProjectGroupError, OutsideProjectPathError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    results_dir = Path(f"/cluster/projects/{project_group}/admin/audit/results/{date}/{relative_path}")
    results_dir / "audit.json"

    logger.debug(
        f"Creating results directory: {results_dir} "
        f"for project group: {project_group}, relative path: {relative_path}"
    )
    results_dir.mkdir(parents=True, exist_ok=True)
    output_file = results_dir / "audit.json"

    # Initialize combined results
    results = {
        "audit_date": timestamp,
        "source_directory": {},
        "directories": {},
        "damply_version": damply_version,
    }
    
    def safe_audit(path: Path) -> dict:
        try:
            logger.info(f"Auditing: {path}")
            audit_obj = DirectoryAudit.from_path(path)
            audit_obj.compute_details(show_progress=True, force=compute_details)
            return {
                "status": "ok",
                "data": audit_obj.to_dict(),
            }
        except Exception as e:
            etype = type(e).__name__
            emsg = str(e)
            stack = traceback.format_exc(limit=5)  # limit frames if needed
            logger.exception(f"Failed audit: {path}")

            return {
                "status": "error",
                "error": f"{etype}: {emsg}",
                "traceback": stack,
            }

    # Audit subdirectories
    for subdir in sorted(directory.iterdir()):
        if subdir.is_dir():
            results["directories"][subdir.name] = safe_audit(subdir)

    # count number of errors
    logger.info(f"Total directories audited: {len(results['directories'])}")
    error_count = sum(
        1 for result in results["directories"].values() if result["status"] == "error"
    )
    if error_count > 0:
        logger.error(f"Total errors encountered: {error_count}")


    # Audit the main source directory
    results["source_directory"] = safe_audit(directory)

    # Save combined results
    output_file.write_text(json.dumps(results, default=str, indent=2))
    logger.info(f"Audit results saved to: {output_file}")


