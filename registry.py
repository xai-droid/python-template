import os
import sys
import json
import logging
import shutil
from typing import Any, Dict, Optional, Tuple

__all__ = [
    "registry_path",
    "load_registry",
    "save_registry",
    "update_registry",
    "get",
    "set",
    "delete",
    "get_python_new_path",
    "check_entry_background",
    "create_entry_background",
    "remove_entry_background",
    "check_shellnew_py",
    "create_shellnew_py",
    "remove_shellnew_py",
]

# Registry file helpers -----------------------------------------------------


def registry_path(path: Optional[str] = None) -> str:
    """Return path to registry file. If path is given, return it; otherwise use registry.json next to this module."""
    if path:
        return os.path.abspath(path)
    return os.path.join(os.path.dirname(__file__), "registry.json")


def load_registry(path: Optional[str] = None) -> Dict[str, Any]:
    """Load registry (JSON). Returns empty dict if file missing or unreadable."""
    p = registry_path(path)
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        logging.exception("Failed to read registry file; returning empty dict.")
        return {}


def save_registry(data: Dict[str, Any], path: Optional[str] = None) -> None:
    """Atomically write the registry dict to disk."""
    p = registry_path(path)
    tmp = p + ".tmp"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # atomic replace
    os.replace(tmp, p)


def update_registry(updates: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
    """
    Merge updates into the stored registry and persist it.
    Returns the new registry dict.
    """
    if not isinstance(updates, dict):
        raise TypeError("updates must be a dict")
    reg = load_registry(path)
    reg.update(updates)
    save_registry(reg, path)
    return reg


def get(key: str, default: Any = None, path: Optional[str] = None) -> Any:
    reg = load_registry(path)
    return reg.get(key, default)


def set(key: str, value: Any, path: Optional[str] = None) -> None:
    reg = load_registry(path)
    reg[key] = value
    save_registry(reg, path)


def delete(key: str, path: Optional[str] = None) -> bool:
    reg = load_registry(path)
    if key in reg:
        del reg[key]
        save_registry(reg, path)
        return True
    return False


# PythonNew script discovery ------------------------------------------------


def get_python_new_path() -> Optional[str]:
    """
    Try to find the installed create_python_new.py script.
    Checks common locations (LOCALAPPDATA install dir, package dir, sys.executable dir
    and repository location). Returns path or None if not found.
    """
    candidates = []
    local_app = os.getenv("LOCALAPPDATA")
    if local_app:
        candidates.append(os.path.join(local_app, "PythonNew", "create_python_new.py"))
    # same dir as this module
    candidates.append(os.path.join(os.path.dirname(__file__), "create_python_new.py"))
    # same dir as the running python executable (scripts area)
    candidates.append(os.path.join(os.path.dirname(sys.executable), "create_python_new.py"))
    # current working directory
    candidates.append(os.path.join(os.getcwd(), "create_python_new.py"))

    for c in candidates:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    return None


# Windows shell integration (injectable winreg for testability) -------------


def _get_winreg(winreg_module):
    """Return a usable winreg-like module or raise."""
    if winreg_module is not None:
        return winreg_module
    try:
        import winreg  # type: ignore
        return winreg
    except Exception as exc:
        raise RuntimeError("winreg not available on this platform") from exc


def check_entry_background(winreg_module=None) -> Tuple[bool, Optional[str]]:
    """
    Check whether the background 'NeuePythonDatei' entry exists.
    Returns (exists: bool, hive: "HKCU" | "HKCR" | None)
    """
    try:
        winreg = _get_winreg(winreg_module)
    except RuntimeError:
        return False, None

    key_name = r"Software\Classes\Directory\Background\shell\NeuePythonDatei"
    # check user hive first
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_name)
        winreg.CloseKey(key)
        return True, "HKCU"
    except Exception:
        pass

    # check system-wide (HKCR) next
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_name)
        winreg.CloseKey(key)
        return True, "HKCR"
    except Exception:
        pass

    return False, None


def create_entry_background(hive: str = "user", winreg_module=None) -> Tuple[bool, str]:
    """
    Create the background context menu entry in the specified hive.
    hive: "user" -> HKEY_CURRENT_USER, "system" -> HKEY_CLASSES_ROOT (requires admin)
    Returns (success, message)
    """
    try:
        winreg = _get_winreg(winreg_module)
    except RuntimeError:
        return False, "winreg not available on this platform"

    script_path = get_python_new_path()
    if not script_path:
        return False, "create_python_new.py not found"

    if hive == "user":
        root = winreg.HKEY_CURRENT_USER
        key_name = r"Software\Classes\Directory\Background\shell\NeuePythonDatei"
    else:
        root = winreg.HKEY_CLASSES_ROOT
        key_name = r"Directory\Background\shell\NeuePythonDatei"  # under HKCR the prefix is different

    try:
        key = winreg.CreateKey(root, key_name)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Neue Python-Datei erstellen…")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, sys.executable)
        winreg.CloseKey(key)

        # command subkey
        key_cmd = winreg.CreateKey(root, key_name + r"\command")
        command = f'"{sys.executable}" "{script_path}" "%V"'
        winreg.SetValueEx(key_cmd, "", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key_cmd)
        return True, f"Entry created in {hive}"
    except PermissionError:
        return False, f"Permission denied creating entry in {hive}"
    except Exception as exc:
        logging.exception("Failed to create background entry")
        return False, str(exc)


def remove_entry_background(hive: str = "user", winreg_module=None) -> Tuple[bool, str]:
    """
    Remove the background context menu entry from specified hive.
    hive: "user" or "system"
    """
    try:
        winreg = _get_winreg(winreg_module)
    except RuntimeError:
        return False, "winreg not available on this platform"

    if hive == "user":
        root = winreg.HKEY_CURRENT_USER
        cmd_path = r"Software\Classes\Directory\Background\shell\NeuePythonDatei\command"
        shell_path = r"Software\Classes\Directory\Background\shell\NeuePythonDatei"
    else:
        root = winreg.HKEY_CLASSES_ROOT
        cmd_path = r"Directory\Background\shell\NeuePythonDatei\command"
        shell_path = r"Directory\Background\shell\NeuePythonDatei"

    try:
        try:
            winreg.DeleteKey(root, cmd_path)
        except FileNotFoundError:
            pass
        try:
            winreg.DeleteKey(root, shell_path)
        except FileNotFoundError:
            return True, "Entry did not exist"
        return True, f"Entry removed from {hive}"
    except PermissionError:
        return False, f"Permission denied removing entry from {hive}"
    except Exception as exc:
        logging.exception("Failed to remove background entry")
        return False, str(exc)


def check_shellnew_py(winreg_module=None) -> Tuple[bool, Optional[str]]:
    """
    Check whether a .py ShellNew FileName is registered.
    Returns (exists, hive) where hive is "HKCR" or "HKCU" or None.
    """
    try:
        winreg = _get_winreg(winreg_module)
    except RuntimeError:
        return False, None

    # check HKCR first
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r".py\ShellNew")
        try:
            winreg.QueryValueEx(key, "FileName")
            winreg.CloseKey(key)
            return True, "HKCR"
        except Exception:
            winreg.CloseKey(key)
            return False, "HKCR"
    except Exception:
        pass

    # HKCU fallback
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.py\ShellNew")
        try:
            winreg.QueryValueEx(key, "FileName")
            winreg.CloseKey(key)
            return True, "HKCU"
        except Exception:
            winreg.CloseKey(key)
            return False, "HKCU"
    except Exception:
        pass

    return False, None


def create_shellnew_py(file_name: str = "NeuePythonDatei.py", hive: str = "system", winreg_module=None) -> Tuple[bool, str]:
    """
    Create a ShellNew entry for .py files. hive: "system"->HKCR, "user"->HKCU
    """
    try:
        winreg = _get_winreg(winreg_module)
    except RuntimeError:
        return False, "winreg not available on this platform"

    if hive == "system":
        root = winreg.HKEY_CLASSES_ROOT
        path = r".py\ShellNew"
    else:
        root = winreg.HKEY_CURRENT_USER
        path = r"Software\Classes\.py\ShellNew"

    try:
        key = winreg.CreateKey(root, path)
        winreg.SetValueEx(key, "FileName", 0, winreg.REG_SZ, file_name)
        winreg.CloseKey(key)
        return True, f".py ShellNew created in {hive}"
    except PermissionError:
        return False, f"Permission denied creating .py ShellNew in {hive}"
    except Exception as exc:
        logging.exception("Failed to create .py ShellNew")
        return False, str(exc)


def remove_shellnew_py(hive: str = "system", winreg_module=None) -> Tuple[bool, str]:
    """
    Remove the .py ShellNew registration from specified hive.
    """
    try:
        winreg = _get_winreg(winreg_module)
    except RuntimeError:
        return False, "winreg not available on this platform"

    if hive == "system":
        root = winreg.HKEY_CLASSES_ROOT
        path = r".py\ShellNew"
    else:
        root = winreg.HKEY_CURRENT_USER
        path = r"Software\Classes\.py\ShellNew"

    try:
        winreg.DeleteKey(root, path)
        return True, f"Removed .py ShellNew from {hive}"
    except FileNotFoundError:
        return True, "Entry did not exist"
    except PermissionError:
        return False, f"Permission denied removing .py ShellNew from {hive}"
    except Exception as exc:
        logging.exception("Failed to remove .py ShellNew")
        return False, str(exc)
