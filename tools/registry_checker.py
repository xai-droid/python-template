from typing import Optional
import logging

def _open_key_safe(winreg, root: Optional[object], path: str):
    """
    Try opening a registry key in a few ways to be tolerant of different winreg-like mocks:
    - winreg.OpenKey(root, path)
    - winreg.OpenKey(path)
    Returns key handle or None.
    """
    try:
        if root is not None:
            try:
                return winreg.OpenKey(root, path)
            except TypeError:
                # OpenKey might accept only path in some mocks
                return winreg.OpenKey(path)
        else:
            return winreg.OpenKey(path)
    except Exception:
        return None

def _close_safe(winreg, key):
    try:
        if hasattr(winreg, "CloseKey"):
            winreg.CloseKey(key)
    except Exception:
        pass

def check_background_entry(winreg=None) -> bool:
    """
    Check for background context menu entry. Returns True if present.
    Accepts an injectable winreg-like object for testing.
    """
    if winreg is None:
        try:
            import winreg as _winreg  # type: ignore
        except Exception:
            logging.info("winreg not available on this platform")
            return False
        winreg = _winreg

    # prefer HKEY_CURRENT_USER but tolerate missing constants
    hcu = getattr(winreg, "HKEY_CURRENT_USER", None)
    possible = [
        r"Software\\Classes\\Directory\\Background\\shell\\NeuePythonDatei_Hintergrund",
        r"Software\\Classes\\Directory\\Background\\shell\\NeuePythonDatei",
    ]
    for p in possible:
        key = _open_key_safe(winreg, hcu, p)
        if not key:
            continue
        try:
            cmd_key = _open_key_safe(winreg, hcu, p + r"\\command")
            if cmd_key:
                _close_safe(winreg, cmd_key)
                _close_safe(winreg, key)
                return True
        finally:
            _close_safe(winreg, key)
    return False

def check_new_py_entry(winreg=None) -> bool:
    """
    Check for .py ShellNew registration. Returns True if present.
    """
    if winreg is None:
        try:
            import winreg as _winreg  # type: ignore
        except Exception:
            logging.info("winreg not available on this platform")
            return False
        winreg = _winreg

    hcr = getattr(winreg, "HKEY_CLASSES_ROOT", None)
    hcu = getattr(winreg, "HKEY_CURRENT_USER", None)

    # try HKCR first, fallback to HKCU "Software\\Classes"
    key = _open_key_safe(winreg, hcr, r".py\\ShellNew")
    if not key:
        key = _open_key_safe(winreg, hcu, r"Software\\Classes\\.py\\ShellNew")
    if not key:
        return False

    try:
        try:
            # Try QueryValueEx(key, "FileName") -- common API
            winreg.QueryValueEx(key, "FileName")
            return True
        except TypeError:
            # Some mocks expect (path, name) where key is path string
            try:
                winreg.QueryValueEx(key, "FileName")
                return True
            except Exception:
                return False
        except Exception:
            return False
    finally:
        _close_safe(winreg, key)