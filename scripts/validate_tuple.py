"""Tuple validation utility for INCUBATOR governance."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.parse_chat_tuple import load_tuple_documents

# Pattern matches: YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###.yml
TUPLE_FILENAME_PATTERN = re.compile(
    r"^[0-9]{2}_W[0-9]{2}_[0-9]{2}_[0-9]{2}__[A-Z0-9_]+__[A-Z0-9_]+__[A-Z0-9_]+__W[0-9]{3}\.yml$"
)

TUPLE_ID_PATTERN = re.compile(
    r"^[0-9]{2}_W[0-9]{2}_[0-9]{2}_[0-9]{2}__[A-Z0-9_]+__[A-Z0-9_]+__[A-Z0-9_]+__W[0-9]{3}$"
)

REQUIRED_TUPLE_FIELDS = {
    "id",
    "date",
    "time_local",
    "iso_week",
    "category",
    "theme",
    "title",
    "wave",
    "status",
    "repo",
    "branch",
    "source_type",
}

ALLOWED_STATUS_VALUES = {"active", "archived", "draft"}
ALLOWED_SOURCE_TYPES = {"chat_tuple", "session_tuple"}


class TupleValidationError(Exception):
    """Exception raised for tuple validation failures."""

    pass


def validate_tuple_filename(filename: str) -> None:
    """Validate tuple filename matches naming convention.
    
    Raises:
        TupleValidationError: If filename doesn't match pattern.
    """
    if not TUPLE_FILENAME_PATTERN.match(filename):
        raise TupleValidationError(
            f"Tuple filename '{filename}' doesn't match naming convention: "
            "YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###.yml"
        )


def validate_tuple_id(tuple_id: str) -> None:
    """Validate tuple ID matches naming convention.
    
    Raises:
        TupleValidationError: If ID doesn't match pattern.
    """
    if not TUPLE_ID_PATTERN.match(tuple_id):
        raise TupleValidationError(
            f"Tuple ID '{tuple_id}' doesn't match naming convention: "
            "YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###"
        )


def validate_tuple_fields(tuple_data: dict[str, Any]) -> None:
    """Validate tuple has all required fields.
    
    Raises:
        TupleValidationError: If required fields are missing.
    """
    missing = REQUIRED_TUPLE_FIELDS - set(tuple_data.keys())
    if missing:
        raise TupleValidationError(
            f"Tuple missing required fields: {', '.join(sorted(missing))}"
        )


def validate_tuple_status(status: str) -> None:
    """Validate tuple status is allowed.
    
    Raises:
        TupleValidationError: If status is not allowed.
    """
    if status not in ALLOWED_STATUS_VALUES:
        raise TupleValidationError(
            f"Tuple status '{status}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_STATUS_VALUES))}"
        )


def validate_tuple_source_type(source_type: str) -> None:
    """Validate tuple source_type is allowed.
    
    Raises:
        TupleValidationError: If source_type is not allowed.
    """
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise TupleValidationError(
            f"Tuple source_type '{source_type}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_SOURCE_TYPES))}"
        )


def validate_tuple(tuple_data: dict[str, Any], filename: str | None = None) -> None:
    """Validate a complete tuple document.
    
    Args:
        tuple_data: Tuple document data
        filename: Optional filename for validation
    
    Raises:
        TupleValidationError: If any validation fails.
    """
    if filename:
        validate_tuple_filename(filename)
    
    validate_tuple_fields(tuple_data)
    validate_tuple_id(tuple_data["id"])
    validate_tuple_status(tuple_data["status"])
    validate_tuple_source_type(tuple_data["source_type"])
    
    # Validate ID matches filename (if provided)
    if filename:
        expected_id = filename.replace(".yml", "")
        if tuple_data["id"] != expected_id:
            raise TupleValidationError(
                f"Tuple ID '{tuple_data['id']}' doesn't match filename '{filename}'"
            )


def validate_all_tuples(incubator_dir: Path | None = None) -> list[dict[str, Any]]:
    """Validate all tuples in incubator directory.
    
    Returns:
        List of valid tuple documents
    
    Raises:
        TupleValidationError: If any tuple fails validation.
    """
    if incubator_dir is None:
        incubator_dir = REPO_ROOT / "incubator"
    
    tuples = load_tuple_documents(incubator_dir)
    
    for tuple_data in tuples:
        # Extract filename from _file path
        file_path = tuple_data.get("_file", "")
        filename = Path(file_path).name if file_path else None
        
        try:
            validate_tuple(tuple_data, filename)
        except TupleValidationError as e:
            raise TupleValidationError(
                f"Validation failed for {file_path or 'unknown'}: {e}"
            ) from e
    
    return tuples


def main() -> int:
    """CLI entry point for tuple validation."""
    try:
        tuples = validate_all_tuples()
        print(f"✅ All {len(tuples)} tuple(s) validated successfully")
        return 0
    except TupleValidationError as e:
        print(f"❌ Tuple validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
