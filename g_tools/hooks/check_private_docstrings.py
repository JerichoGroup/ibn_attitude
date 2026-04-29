"""pre-commit hook that checks for docstrings in private methods."""

# ==================== Imports ====================
from pathlib import Path
import re
import sys
from typing import List


# ==================== Helper - has docstring ====================
def has_docstring(lines: List[str], start_index: int) -> bool:
    """Return True if a docstring is found immediately after the function definition."""

    for i in range(start_index + 1, len(lines)):
        stripped = lines[i].strip()

        if stripped == "" or stripped.startswith("#"):
            continue

        return stripped.startswith('"""') or stripped.startswith("'''")

    return False


# ==================== Main function ====================
def main() -> None:
    """Check Python files for private methods missing docstrings."""

    failed = False

    for path in Path().rglob("*.py"):
        lines = path.read_text().splitlines()

        for i, line in enumerate(lines):
            if re.match(r"\s*def _[A-Za-z0-9_]*\(", line):
                if not has_docstring(lines, i):
                    print(f"{path}:{i+1}: Missing docstring for private method")
                    failed = True

    if failed:
        sys.exit(1)


# ==================== Entrypoint ====================
if __name__ == "__main__":
    main()
