import pytest
from pathlib import Path
from templates import TemplatesManager
from gui import PythonNewGUI

def test_gui_autofill_and_render(tmp_path):
    # skip if tkinter isn't available on this platform
    pytest.importorskip("tkinter")
    templates_dir = tmp_path / "templates"
    tm = TemplatesManager(templates_dir)
    tm.save_template("t.py", "Hello ${name}", metadata={"vars": ["name"]})

    # create GUI hidden and wire it to use temp templates
    gui = PythonNewGUI(str(tmp_path))
    gui.withdraw()
    gui.tm = tm
    gui._populate_list(tm.list_templates())
    gui._select_template_by_name("t.py")

    # Auto-fill -> there should be a 'name' row
    gui._auto_fill_vars()
    assert any(k.get().strip() == "name" for k, v in gui.vars_entries.values())

    # Render preview should substitute the value (auto-filled or placeholder)
    gui._render_preview()
    content = gui.preview.get("1.0", "end")
    assert "Hello" in content

    gui.destroy()