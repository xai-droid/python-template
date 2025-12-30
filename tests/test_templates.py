import json
from pathlib import Path
from templates import TemplatesManager, random_name
import tempfile

def test_templates_crud_and_render(tmp_path):
    td = tmp_path / "templates"
    tm = TemplatesManager(td)
    # create
    name = "t1.py"
    content = "Hello ${who}"
    tm.create_template(name, content, {"vars": ["who"], "description": "desc"})
    assert name in tm.list_templates()
    # render with variable
    rendered = tm.render_template(name, {"who": "Alice"})
    assert "Hello Alice" in rendered
    # nested variable in value
    tm.save_template("nested.py", "A: ${a} B: ${b}", metadata={"vars": ["a","b"]})
    # b uses ${a}
    out = tm.render_template("nested.py", {"a": "X", "b": "${a}Y"})
    assert "B: XY" in out
    # rename
    tm.rename_template(name, "t2.py")
    assert "t2.py" in tm.list_templates()
    assert "t1.py" not in tm.list_templates()
    # delete
    assert tm.delete_template("t2.py")
    assert "t2.py" not in tm.list_templates()import json
from pathlib import Path
from templates import TemplatesManager, random_name
import tempfile

def test_templates_crud_and_render(tmp_path):
    td = tmp_path / "templates"
    tm = TemplatesManager(td)
    # create
    name = "t1.py"
    content = "Hello ${who}"
    tm.create_template(name, content, {"vars": ["who"], "description": "desc"})
    assert name in tm.list_templates()
    # render with variable
    rendered = tm.render_template(name, {"who": "Alice"})
    assert "Hello Alice" in rendered
    # nested variable in value
    tm.save_template("nested.py", "A: ${a} B: ${b}", metadata={"vars": ["a","b"]})
    # b uses ${a}
    out = tm.render_template("nested.py", {"a": "X", "b": "${a}Y"})
    assert "B: XY" in out
    # rename
    tm.rename_template(name, "t2.py")
    assert "t2.py" in tm.list_templates()
    assert "t1.py" not in tm.list_templates()
    # delete
    assert tm.delete_template("t2.py")
    assert "t2.py" not in tm.list_templates()