"""
Fix Unicode characters in seed scripts for Windows compatibility.
Session: 20251111-234532
"""
import re
from pathlib import Path

# Unicode replacements
REPLACEMENTS = {
    "\u2713": "OK",  # ✓
    "\u2714": "OK",  # ✔
    "\u2705": "OK",  # ✅
    "\u274c": "ERROR",  # ❌
    "\u274e": "X",  # ❎
    "\u26a0": "WARNING",  # ⚠
    "\u2192": "->",  # →
    "\u2265": ">=",  # ≥
    "\u2264": "<=",  # ≤
}


def fix_file(filepath):
    """Fix Unicode characters in a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        for unicode_char, replacement in REPLACEMENTS.items():
            content = content.replace(unicode_char, replacement)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {filepath.name}")
            return True
        else:
            print(f"No changes: {filepath.name}")
            return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


if __name__ == "__main__":
    backend_dir = Path(__file__).parent.parent
    scripts_dir = backend_dir / "app" / "scripts"

    print("Fixing Unicode characters in seed scripts...\n")

    files_to_fix = list(scripts_dir.glob("seed*.py")) + list(
        scripts_dir.glob("populate*.py")
    )

    fixed_count = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1

    print(f"\nFixed {fixed_count} file(s)")
