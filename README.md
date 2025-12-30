# py-new-file

Simple utility to create new Python files from templates with a small GUI and registry for persistent settings.

## Overview
- Launches a Tkinter GUI (class `PythonNewGUI` in `gui.py`) to create files from templates.
- Manages templates via `templates.TemplatesManager`.
- Persists simple settings/data via `registry` (JSON file).
- `main.py` boots the GUI and accepts an optional target directory argument.

## Requirements
- Python 3.8+
- Tkinter (standard with most Python installs)
- No external dependencies.

## Installation
Clone the repo:
```powershell
cd C:\Users\alexh\source\repos
git clone <repo-url> py-new-file
cd py-new-file
```

Run with your system Python:
```powershell
python main.py
# or specify a folder to create new files in:
python main.py "C:\path\to\project"
```

## Files & Layout
- main.py — application entry point; shows errors with Tkinter dialogs.
- gui.py — GUI implementation (must expose `PythonNewGUI(target_dir)`).
- registry.py — JSON-backed registry helpers: `registry_path`, `load_registry`, `save_registry`, `update_registry`, `get`, `set`, `delete`.
- templates.py — `TemplatesManager` for template CRUD, rendering and metadata.
- templates/ — template files (created/managed by TemplatesManager).
- templates/templates.json — metadata for templates (created automatically).

Project root (example):
```
c:\Users\alexh\source\repos\py-new-file
├─ main.py
├─ gui.py
├─ registry.py
├─ templates.py
└─ templates\
   ├─ starter.py
   └─ templates.json
```

## Usage

### CLI
- python main.py [target_dir]
  - If target_dir omitted, uses current working directory.
  - If target_dir is invalid, shows a Tkinter error dialog and exits with code 2.
  - If GUI module import fails, shows a Tkinter error dialog and exits with code 1.

(main.py does not implement additional CLI flags by default; extend as needed.)

### GUI
- The GUI should accept a target directory (passed from `main.py`) and provide controls to:
  - Select a template
  - Render with variable substitution
  - Create/save/rename/delete templates
  - Create a new file in the target directory from a rendered template

Behavior:
- Errors during GUI load or runtime show a Tkinter error dialog (via `show_error` in `main.py`).
- The GUI main loop is wrapped to surface unexpected exceptions.

## templates.TemplatesManager (features)
- Initialize with a templates directory path (Path or str).
- Ensures templates directory exists and creates a default `starter.py` if no templates present.
- Methods:
  - list_templates() -> List[str]
  - list_templates_with_meta() -> List[dict] (name + meta)
  - load_template(name, with_meta=False) -> content or (content, meta)
  - save_template(name, content, metadata=None, overwrite=True)
  - create_template(name, content, metadata=None)  # fails if exists
  - delete_template(name) -> bool
  - rename_template(old_name, new_name)
  - render_template(name, vars=None) -> str (uses string.Template.safe_substitute)
  - get_metadata(name) -> dict
  - update_metadata(name, metadata)
- Metadata stored in templates/templates.json with created_at/updated_at timestamps.

Template rendering:
- Uses Python's string.Template with safe_substitute to avoid exceptions on missing keys.
- Default starter template includes ${name} and ${description} placeholders.

## registry (features)
- Functions:
  - registry_path(path=None) -> str (path to JSON registry; default is registry.json next to module)
  - load_registry(path=None) -> dict
  - save_registry(data, path=None) -> None
  - update_registry(updates, path=None) -> dict (merges updates and persists)
  - get(key, default=None, path=None) -> Any
  - set(key, value, path=None) -> None
  - delete(key, path=None) -> bool
- Registry file defaults to `registry.json` adjacent to `registry.py` (or custom path can be passed).
- Read/write is resilient: missing/corrupt file yields an empty dict; writes are atomic (tmp + replace).

## Troubleshooting
- ImportError: cannot import name 'update_registry'
  - Ensure `registry.py` defines `update_registry` and it is exported (present in module namespace).
  - Confirm Python is importing the project copy (no name shadowing by another installed package named `registry`).
    - Run: `python -c "import registry, inspect; print(registry.__file__); print(dir(registry))"`
- Tkinter error dialogs not shown:
  - Ensure Tkinter available; on some Windows Pythons, install the optional tcl/tk support or use the system Python.
- Template variables not substituted:
  - Provide a dict of vars to `render_template`; missing keys will result in unchanged placeholders with safe_substitute (or raw content fallback if substitution fails).

## Extending / Development Notes
- Add CLI flags (e.g., --templates-dir, --no-gui, --list-templates) by parsing `sys.argv` or using argparse in main.py.
- Add unit tests for `templates.py` and `registry.py`.
- Keep GUI import errors user-friendly (main.py already displays a messagebox).
- Consider moving registry default to user config folder (e.g., `%APPDATA%/py-new-file`) if per-user persistence is desired.

## Examples

Create a file from a template programmatically:
```python
from templates import TemplatesManager
tm = TemplatesManager("templates")
content = tm.render_template("starter.py", {"name":"MyScript","description":"Demo"})
open(r"C:\path\to\project\myscript.py","w",encoding="utf-8").write(content)
```

Update registry:
```python
import registry
registry.update_registry({"last_target": r"C:\path\to\project"})
```

If you want a README with additional CLI flags or a more detailed developer guide, tell me which features to add.

