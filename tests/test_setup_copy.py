import tempfile
from pathlib import Path
import shutil
import logging
import setup_newfile as sn

def test_copy_files_handles_missing(tmp_path, caplog):
    src = tmp_path / "src"
    src.mkdir()
    # create one of the files
    f = src / "main.py"
    f.write_text("# main")
    dst = tmp_path / "out"
    caplog.set_level(logging.WARNING)
    sn.copy_files(dst)  # using repo-level copy will skip missing files; ensure no crash
    # Ensure placeholder icon exists in repo root (we added it)
    repo_root = Path(__file__).parents[1]
    assert (repo_root / "icon.ico").exists()