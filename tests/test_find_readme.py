from pathlib import Path

from damply.utils.find_readme import find_readme


def test_find_readme_in_root_case_insensitive(tmp_path: Path) -> None:
	# Create a mixed-case README in root
	readme = tmp_path / "ReAdMe.MD"
	readme.write_text("#DESC: example\n")

	found = find_readme(tmp_path)
	assert found is not None
	assert found.name == readme.name


def test_find_readme_in_docs_case_insensitive(tmp_path: Path) -> None:
	# No root README, but one in docs with mixed case
	docs = tmp_path / "docs"
	docs.mkdir()
	readme = docs / "readME.txt"
	readme.write_text("#DESC: example\n")

	found = find_readme(tmp_path)
	assert found is not None
	assert found.name == readme.name
	assert found.parent == docs


def test_find_readme_none(tmp_path: Path) -> None:
	assert find_readme(tmp_path) is None

