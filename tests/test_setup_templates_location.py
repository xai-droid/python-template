import shutil
from pathlib import Path
import setup_newfile as sn

def test_templates_stay_in_templates_dir(tmp_path):
    dst = tmp_path / "install"
    dst.mkdir()
    # perform copy
    install_dir, copied = sn.copy_files(dst)
    # templates dir should exist
    templates_dir = Path(install_dir) / "templates"
    assert templates_dir.exists() and templates_dir.is_dir()
    # for each template file, ensure it was NOT copied to install root
    for t in templates_dir.glob("*.py"):
        assert not (Path(install_dir) / t.name).exists()