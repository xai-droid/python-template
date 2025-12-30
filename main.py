import sys
import os
import traceback
from pathlib import Path
from typing import List, Optional

def _show_error(msg: str):
    """Show an error message; avoid modal dialogs during tests or headless runs."""
    # If running under pytest / CI, avoid creating a GUI dialog
    if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("CI"):
        print(f"ERROR: {msg}", file=sys.stderr)
        return
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("py-new-file", msg)
        root.destroy()
    except Exception:
        print(f"ERROR: {msg}", file=sys.stderr)

def _try_fallback_helper(argv: List[str]) -> int:
    """Attempt to run the headless helper if GUI import/launch fails."""
    try:
        # call helper.main with argv-like args (skip script name)
        import create_python_new as helper
        return helper.main(argv[1:]) or 0
    except Exception:
        print("Fallback helper failed:", file=sys.stderr)
        traceback.print_exc()
        return 1

def main(argv: Optional[List[str]] = None) -> int:
    """
    Start the GUI. argv can be provided (list) or will default to sys.argv.
    Returns exit code (0 on success, non-zero on fatal error).
    """
    argv = list(argv) if argv is not None else list(sys.argv)
    target = None
    if len(argv) > 1:
        target = argv[1]

    try:
        # Import GUI lazily so importing main on non-GUI environments is safe.
        from gui import PythonNewGUI
    except Exception as exc:
        # Print traceback for debugging and try headless fallback
        print("Failed importing GUI:", file=sys.stderr)
        traceback.print_exc()
        _show_error(f"Unable to start GUI: {exc}\n\nSee console for traceback.")
        return _try_fallback_helper(argv)

    try:
        # If a target directory is provided, pass it; otherwise GUI will restore last used.
        gui = PythonNewGUI(target or ".")
        gui.mainloop()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print("Unhandled error while running GUI:", file=sys.stderr)
        traceback.print_exc()
        _show_error(f"Unhandled error in application: {exc}\n\nSee console for traceback.")
        # try fallback helper
        return _try_fallback_helper(argv)

if __name__ == "__main__":
    raise SystemExit(main())
