#!/usr/bin/env python
import sys
import os
import time
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATES_DIR = ROOT / "templates"
TEMPLATE_FILE = TEMPLATES_DIR / "NeuePythonDatei.py"
EMPTY_FILE = TEMPLATES_DIR / "LeerePythonDatei.py"

def _unique_name(prefix: str) -> str:
    return f"{prefix}_{int(time.time())}.py"

def create_from(src: Path, target_dir: Path, name_prefix: str):
    target_dir.mkdir(parents=True, exist_ok=True)
    name = _unique_name(name_prefix)
    dest = target_dir / name
    if src.exists():
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        # fallback minimal content
        if "Template" in name_prefix:
            dest.write_text("# template\n", encoding="utf-8")
        else:
            dest.write_text("# empty python file\n", encoding="utf-8")
    print(f"Created {dest}")
    return dest

def main(argv=None):
    """
    argv: optional list of arguments (like sys.argv[1:])
    Usage: main([target_dir, mode])
    mode == "t" => create template-based file
    mode == "l" => create empty file
    If argv is None, uses sys.argv.
    Returns exit code (0 success).
    """
    if argv is None:
        argv = sys.argv[1:]
    target = Path(argv[0]) if len(argv) > 0 else Path.cwd()
    mode = argv[1] if len(argv) > 1 else None
    if mode == "t":
        create_from(TEMPLATE_FILE, target, "NeuePythonDatei_Template")
        return 0
    if mode == "l":
        create_from(EMPTY_FILE, target, "NeuePythonDatei_Leer")
        return 0
    # fallback: start GUI app (if available)
    try:
        from main import main as run_main
        # call GUI main with the same argv (include script name fallback)
        return run_main([sys.argv[0], str(target)]) or 0
    except Exception as e:
        print(f"Cannot start GUI: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())