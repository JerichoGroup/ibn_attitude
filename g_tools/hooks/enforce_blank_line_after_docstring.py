"""Enforce a blank line after every function docstring."""

# ==================== Imports ====================
import ast
from pathlib import Path
import sys


# ==================== Helper - process file ====================
def process_file(path: Path) -> bool:
    """Return True if the file at path was modified."""

    original = path.read_text().splitlines(keepends=True)
    modified = original.copy()

    try:
        tree = ast.parse("".join(original))
    except SyntaxError:
        return False

    func_nodes = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    inserts = []

    for node in func_nodes:
        if not node.body:
            continue

        first_stmt = node.body[0]

        if not isinstance(first_stmt, ast.Expr) or not isinstance(first_stmt.value, ast.Str):
            continue

        end = first_stmt.end_lineno
        if end is None:
            return False

        docstring_end_line = end
        next_line_index = docstring_end_line

        if next_line_index < len(modified):
            if modified[next_line_index].strip() != "":
                inserts.append(next_line_index)

    for idx in reversed(inserts):
        modified.insert(idx, "\n")

    if modified != original:
        path.write_text("".join(modified))
        return True

    return False


# ==================== Main function ====================
def main() -> None:
    """Enforce a blank line after docstrings in Python files."""

    changed = False

    for filename in sys.argv[1:]:
        path = Path(filename)
        if path.suffix == ".py":
            if process_file(path):
                changed = True

    if changed:
        sys.exit(1)

    sys.exit(0)


# ==================== Entrypoint ====================
if __name__ == "__main__":
    main()
