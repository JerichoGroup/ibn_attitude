"""pre-commit hook that checks for docstrings in private methods."""

# ==================== Imports ====================
import ast
from pathlib import Path
import sys
from typing import List


# ==================== Helper - find undocumented ====================
def find_undocumented(path: Path) -> List[int]:
    """Return the line numbers of private functions missing a docstring."""

    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return []

    missing: List[int] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        if not node.name.startswith("_"):
            continue

        if ast.get_docstring(node) is None:
            missing.append(node.lineno)

    return missing


# ==================== Main function ====================
def main() -> None:
    """Check Python files for private methods missing docstrings."""

    failed = False

    for filename in sys.argv[1:]:
        path = Path(filename)
        if path.suffix != ".py":
            continue

        for lineno in find_undocumented(path):
            print(f"{path}:{lineno}: Missing docstring for private method")
            failed = True

    if failed:
        sys.exit(1)


# ==================== Entrypoint ====================
if __name__ == "__main__":
    main()
