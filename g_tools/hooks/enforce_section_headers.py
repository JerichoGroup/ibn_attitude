"""Pre-commit hook that enforces standardized section header formatting."""

# ==================== Imports ====================
from pathlib import Path
import re
import sys


# ==================== Helper - format header ====================
def format_header(text: str) -> str:
    """Return a properly formatted section header line."""

    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
    left = "=" * 20
    right = "=" * 20
    return f"# {left} {text} {right}\n"


# ==================== Helper - process file ====================
def process_file(path: Path) -> bool:
    """Return True if the file was modified."""

    original = path.read_text().splitlines(keepends=True)
    modified: list[str] = []
    changed = False

    header_re = re.compile(r"^#\s*=?=+\s*(.*?)\s*=+")
    found_first_header = False

    i = 0
    while i < len(original):
        line = original[i]

        match = header_re.match(line)
        if match:
            text = match.group(1)
            new_header = format_header(text)

            required_blanks = 1 if not found_first_header else 2
            found_first_header = True

            existing_blanks = 0
            j = len(modified) - 1
            while j >= 0 and modified[j].strip() == "":
                existing_blanks += 1
                j -= 1

            if existing_blanks != required_blanks:
                for _ in range(existing_blanks):
                    modified.pop()
                for _ in range(required_blanks):
                    modified.append("\n")
                changed = True

            if not modified or modified[-1] != new_header:
                modified.append(new_header)
                if new_header != line:
                    changed = True

            i += 1
            continue

        modified.append(line)
        i += 1

    if modified != original:
        path.write_text("".join(modified))
        print(f"Fixed section headers in: {path}")
        return True

    return changed


# ==================== Main function ====================
def main() -> None:
    """Enforce section header formatting in Python files."""

    changed_any = False

    for filename in sys.argv[1:]:
        path = Path(filename)
        if path.suffix == ".py":
            if process_file(path):
                changed_any = True

    if changed_any:
        sys.exit(1)

    sys.exit(0)


# ==================== Entrypoint ====================
if __name__ == "__main__":
    main()
