import subprocess
import sys
from pathlib import Path
import tempfile

SCRIPT = Path(__file__).parents[1] / "create_python_new.py"

def test_create_modes(tmp_path):
    tgt = tmp_path / "out"
    tgt.mkdir()
    subprocess.run([sys.executable, str(SCRIPT), str(tgt), "t"], check=True)
    assert any(tgt.glob("NeuePythonDatei*"))
    subprocess.run([sys.executable, str(SCRIPT), str(tgt), "l"], check=True)
    assert any(tgt.glob("NeuePythonDatei_Leer*"))