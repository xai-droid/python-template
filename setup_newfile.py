import os
import shutil
import logging
import argparse
import sys
import subprocess
import time
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import registry

# --- Logging ---
LOG_FILE = Path.home() / "python_new_setup.log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# --- Installationspfad ---
DEFAULT_INSTALL_DIR = Path.home() / "AppData" / "Local" / "PythonNew"
INSTALL_DIR = None

def select_install_dir():
    global INSTALL_DIR
    if INSTALL_DIR is None:
        root = tk.Tk()
        root.withdraw()
        dir_choice = filedialog.askdirectory(title="Installationspfad wählen", initialdir=DEFAULT_INSTALL_DIR)
        if not dir_choice:
            messagebox.showerror("Abbruch", "Kein Pfad gewählt.")
            sys.exit(1)
        INSTALL_DIR = Path(dir_choice)
    return INSTALL_DIR

# --- Dateien / Module ---
MODULES = ["main.py", "gui.py", "registry.py", "templates.py", "cache.py", "create_python_new.py", "registry_gui.py"]
WRAPPER = "create_python_new.bat"
TEMPLATE_DIR = "templates"
DUMMY_FILE = "dummy.py"
ICON_FILE = "icon.ico"

DEFAULT_INSTALL_SUBDIR = "PythonNew"


def _default_install_dir() -> Path:
    base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / DEFAULT_INSTALL_SUBDIR


def _copy_list(src: Path, dst: Path, files: Iterable[str]) -> List[str]:
    copied = []
    dst.mkdir(parents=True, exist_ok=True)
    for name in files:
        s = src / name
        d = dst / name
        if s.exists():
            shutil.copy(s, d)
            copied.append(str(d))
        else:
            logging.warning("Skipping missing file: %s", s)
    return copied


def _create_wrapper(install_dir: Path) -> Path:
    """
    Create a small batch wrapper that runs the installed create_python_new.py.
    Tries 'py -3' first, then 'python'.
    """
    wrapper = install_dir / WRAPPER
    script = install_dir / "create_python_new.py"
    content = (
        "@echo off\r\n"
        "REM Wrapper to run create_python_new.py from the installation directory.\r\n"
        "set SCRIPT=%~dp0create_python_new.py\r\n"
        "py -3 \"%SCRIPT%\" %*\r\n"
        "if %ERRORLEVEL% NEQ 0 (\r\n"
        "  python \"%SCRIPT%\" %*\r\n"
        ")\r\n"
    )
    wrapper.write_text(content, encoding="utf-8")
    return wrapper


def _copy_templates(src: Path, dst: Path) -> List[str]:
    src_t = src / TEMPLATE_DIR
    dst_t = dst / TEMPLATE_DIR
    if not src_t.exists():
        return []
    shutil.copytree(src_t, dst_t, dirs_exist_ok=True)
    copied = [str(p) for p in dst_t.iterdir() if p.is_file() and p.suffix == ".py"]
    return copied


def _install_shellnew_template_to_system(template_src: Path) -> Tuple[bool, str]:
    """
    Attempt to copy a template to %SystemRoot%\\ShellNew (requires admin).
    Returns (ok, message).
    """
    sys_root = os.getenv("SystemRoot")
    if not sys_root:
        return False, "%SystemRoot% not defined"
    shellnew_dir = Path(sys_root) / "ShellNew"
    try:
        shellnew_dir.mkdir(parents=True, exist_ok=True)
        dst = shellnew_dir / template_src.name
        shutil.copy(template_src, dst)
        return True, f"Copied to {dst}"
    except PermissionError:
        return False, "Permission denied copying to %SystemRoot%\\ShellNew"
    except Exception as exc:
        logging.exception("Failed copying to ShellNew")
        return False, str(exc)


def copy_files(install_dir: Optional[Path] = None) -> Tuple[Path, List[str]]:
    """
    Copy the package files into install_dir (default is LOCALAPPDATA/PythonNew).
    Returns (install_dir, list_of_copied_paths).
    """
    src = Path(__file__).parent
    dst = Path(install_dir or _default_install_dir())
    dst.mkdir(parents=True, exist_ok=True)

    copied = []
    # copy modules and helper files
    copied += _copy_list(src, dst, MODULES + [DUMMY_FILE, ICON_FILE])
    # wrapper batch
    copied.append(str(_create_wrapper(dst)))
    # copy templates folder and also top-level templates
    copied += _copy_templates(src, dst)

    logging.info("Installed files to %s", dst)
    return dst, copied


def _explorer_running() -> bool:
    """Return True if explorer.exe is currently listed in tasklist."""
    if os.name != "nt":
        return False
    try:
        # request text with a robust decoding to avoid UnicodeDecodeError
        r = subprocess.run(
            ["tasklist", "/fi", "imagename eq explorer.exe"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        out = (r.stdout or "") + (r.stderr or "")
        return "explorer.exe" in out and "INFO:" not in out  # simple heuristic
    except Exception:
        return False


def restart_explorer(wait_seconds: int = 15) -> Tuple[bool, str]:
    """
    Restart Windows Explorer by killing and relaunching explorer.exe.
    Blocks until explorer.exe is detected again or timeout elapses.
    Returns (success, message).
    """
    if os.name != "nt":
        return False, "Not running on Windows"

    # kill explorer (may fail if none running)
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # small pause to allow termination
    end = time.time() + min(5, wait_seconds)
    while time.time() < end:
        if not _explorer_running():
            break
        time.sleep(0.1)

    # start explorer
    try:
        subprocess.Popen(["explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        logging.exception("Failed to start explorer.exe")
        return False, f"Failed to start explorer.exe: {exc}"

    # wait until it's running (up to wait_seconds)
    end = time.time() + wait_seconds
    while time.time() < end:
        if _explorer_running():
            return True, "Explorer restarted"
        time.sleep(0.2)

    return False, "Explorer did not appear within timeout"


def install(
    install_dir: Optional[Path] = None,
    apply_registry: bool = True,
    shellnew_hive: str = "user",
    background_hive: str = "user",
    restart_explorer_after: bool = False,
) -> Tuple[bool, str]:
    """
    High-level install operation.
    - install_dir: Path to install to (default LOCALAPPDATA/PythonNew)
    - apply_registry: whether to create background/ShellNew entries
    - shellnew_hive: "user" or "system" (system will try copying template to %SystemRoot%\\ShellNew)
    - background_hive: "user" or "system"
    - restart_explorer_after: if True and on Windows, restart Explorer after install and wait for it.
    Returns (success, message)
    """
    try:
        dst, copied = copy_files(install_dir)
    except Exception as exc:
        logging.exception("Install failed while copying files")
        return False, f"Copy failed: {exc}"

    # apply registry entries if requested
    if apply_registry:
        ok_bg, msg_bg = registry.create_entry_background(hive=background_hive)
        if not ok_bg:
            logging.warning("Background entry creation failed: %s", msg_bg)

        tpl_name = "NeuePythonDatei.py"
        if shellnew_hive == "system":
            src_tpl = dst / TEMPLATE_DIR / tpl_name
            if src_tpl.exists():
                ok_copy, copy_msg = _install_shellnew_template_to_system(src_tpl)
                if not ok_copy:
                    logging.warning("Could not copy template to ShellNew system dir: %s", copy_msg)
            ok_sn, msg_sn = registry.create_shellnew_py(tpl_name, hive="system")
        else:
            ok_sn, msg_sn = registry.create_shellnew_py(tpl_name, hive="user")
        if not ok_sn:
            logging.warning("ShellNew creation failed: %s", msg_sn)

    # optionally restart Explorer (Windows) and wait
    re_msg = ""
    if restart_explorer_after:
        ok_re, msg_re = restart_explorer(wait_seconds=15)
        re_msg = f"; Explorer restart: {ok_re} - {msg_re}"
        if not ok_re:
            logging.warning("Explorer restart failed: %s", msg_re)

    return True, f"Installed to {dst}{re_msg}"


def uninstall(install_dir: Optional[Path] = None, remove_files: bool = True, remove_registry: bool = True, restart_explorer_after: bool = False) -> Tuple[bool, str]:
    """
    Uninstall: remove registry entries and optionally remove installed files.
    restart_explorer_after: restart Explorer on Windows when True.
    """
    dst = Path(install_dir or _default_install_dir())
    msgs = []
    if remove_registry:
        ok_bg, msg_bg = registry.remove_entry_background(hive="user")
        msgs.append(f"Background(user): {ok_bg} {msg_bg}")
        ok_bg2, msg_bg2 = registry.remove_entry_background(hive="system")
        msgs.append(f"Background(system): {ok_bg2} {msg_bg2}")
        ok_sn, msg_sn = registry.remove_shellnew_py(hive="user")
        msgs.append(f"ShellNew(user): {ok_sn} {msg_sn}")
        ok_sn2, msg_sn2 = registry.remove_shellnew_py(hive="system")
        msgs.append(f"ShellNew(system): {ok_sn2} {msg_sn2}")

    if remove_files:
        try:
            if dst.exists() and dst.is_dir():
                shutil.rmtree(dst)
                msgs.append(f"Removed files at {dst}")
        except Exception as exc:
            logging.exception("Failed to remove install dir")
            return False, f"Failed removing files: {exc}"

    re_msg = ""
    if restart_explorer_after:
        ok_re, msg_re = restart_explorer(wait_seconds=15)
        re_msg = f"; Explorer restart: {ok_re} - {msg_re}"
        if not ok_re:
            logging.warning("Explorer restart failed: %s", msg_re)
    return True, "; ".join(msgs) + re_msg


def status(install_dir: Optional[Path] = None) -> str:
    dst = Path(install_dir or _default_install_dir())
    lines = []
    lines.append(f"Install dir: {dst} (exists: {dst.exists()})")
    ok_bg, hive_bg = registry.check_entry_background()
    lines.append(f"Background entry: {ok_bg} (hive: {hive_bg})")
    ok_sn, hive_sn = registry.check_shellnew_py()
    lines.append(f".py ShellNew: {ok_sn} (hive: {hive_sn})")
    return "\n".join(lines)


def _run_setup_gui() -> int:
    """Launch a small Tk-based setup GUI (returns 0 on normal exit)."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except Exception:
        print("Tkinter not available, cannot show GUI.", file=sys.stderr)
        return 1

    root = tk.Tk()
    root.title("PythonNew Installer")
    root.geometry("640x360")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Install path:").grid(row=0, column=0, sticky="w")
    install_var = tk.StringVar(value=str(_default_install_dir()))
    install_entry = ttk.Entry(frm, textvariable=install_var, width=60)
    install_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
    ttk.Button(frm, text="Browse...", command=lambda: _browse_dir(install_var, root)).grid(row=0, column=2, padx=6)

    apply_reg_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(frm, text="Apply registry entries", variable=apply_reg_var).grid(row=1, column=1, sticky="w", pady=(6,0))

    ttk.Label(frm, text=".py ShellNew hive:").grid(row=2, column=0, sticky="w", pady=(6,0))
    shellnew_hive = ttk.Combobox(frm, values=["user", "system"], state="readonly", width=10)
    shellnew_hive.set("user")
    shellnew_hive.grid(row=2, column=1, sticky="w", pady=(6,0))

    ttk.Label(frm, text="Background menu hive:").grid(row=3, column=0, sticky="w", pady=(6,0))
    background_hive = ttk.Combobox(frm, values=["user", "system"], state="readonly", width=10)
    background_hive.set("user")
    background_hive.grid(row=3, column=1, sticky="w", pady=(6,0))

    # Restart Explorer option (created before callbacks so it's accessible)
    restart_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(frm, text="Restart Explorer after operation (Windows only)", variable=restart_var).grid(row=4, column=1, sticky="w", pady=(6,0))

    output = tk.Text(frm, height=10, wrap="word")
    output.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(8,0))
    frm.rowconfigure(5, weight=1)
    frm.columnconfigure(1, weight=1)

    def _log(msg: str):
        output.insert("end", msg + "\n")
        output.see("end")

    def _flash_congrats():
        """Non-modal flash window shown after successful install + explorer restart."""
        win = tk.Toplevel(root)
        win.title("Congratulations")
        win.attributes("-topmost", True)
        win.geometry("+%d+%d" % (root.winfo_rootx() + 60, root.winfo_rooty() + 60))
        lbl = ttk.Label(win, text="Congratulations — PythonNew was installed", font=("Segoe UI", 12, "bold"), padding=18)
        lbl.pack()

        def _blink(count=6):
            # alternate background color
            bg = "#ffd700" if (count % 2) else "#ffffff"
            try:
                lbl.config(background=bg)
                win.config(background=bg)
            except Exception:
                pass
            if count > 0:
                win.after(300, _blink, count - 1)
            else:
                try:
                    win.destroy()
                except Exception:
                    pass

        win.after(200, _blink, 6)

    def do_install():
        path = Path(install_var.get()) if install_var.get() else None
        ok, msg = install(install_dir=path, apply_registry=apply_reg_var.get(),
                          shellnew_hive=shellnew_hive.get(), background_hive=background_hive.get(),
                          restart_explorer_after=restart_var.get())
        _log(f"Install: {ok} - {msg}")
        if ok:
            if restart_var.get():
                # install() already waited for explorer restart; flash congrats now
                _flash_congrats()
            else:
                messagebox.showinfo("Install", msg)
        else:
            messagebox.showerror("Install failed", msg)

    def do_uninstall():
        path = Path(install_var.get()) if install_var.get() else None
        if not messagebox.askyesno("Uninstall", "Really uninstall (will remove registry entries and files)?"):
            return
        ok, msg = uninstall(install_dir=path, remove_files=True, remove_registry=True, restart_explorer_after=restart_var.get())
        _log(f"Uninstall: {ok} - {msg}")
        if ok:
            if restart_var.get():
                _flash_congrats()
            else:
                messagebox.showinfo("Uninstall", msg)
        else:
            messagebox.showerror("Uninstall failed", msg)

    def do_status():
        path = Path(install_var.get()) if install_var.get() else None
        st = status(install_dir=path)
        _log(f"Status:\n{st}")
        messagebox.showinfo("Status", st)

    ttk.Button(frm, text="Install", command=do_install).grid(row=4, column=0, pady=8)
    ttk.Button(frm, text="Uninstall", command=do_uninstall).grid(row=4, column=1, pady=8)
    ttk.Button(frm, text="Status", command=do_status).grid(row=4, column=2, pady=8)
    ttk.Button(frm, text="Close", command=root.destroy).grid(row=7, column=2, sticky="e", pady=(8,0))

    def _browse_dir(var, parent):
        from tkinter import filedialog
        d = filedialog.askdirectory(parent=parent, initialdir=var.get() or str(_default_install_dir()))
        if d:
            var.set(d)

    root.mainloop()
    return 0


def _cli():
    # If run without args, open the GUI installer
    if len(sys.argv) <= 1:
        return _run_setup_gui()

    p = argparse.ArgumentParser(description="Install / uninstall PythonNew into LOCALAPPDATA (and optionally registry entries).")
    p.add_argument("action", choices=["install", "uninstall", "status"], help="Action")
    p.add_argument("--path", "-p", help="Installation path (defaults to %%LOCALAPPDATA%%\\PythonNew)")
    p.add_argument("--no-registry", action="store_true", help="Do not create registry entries")
    p.add_argument("--shellnew-hive", choices=["user", "system"], default="user", help="Where to create .py ShellNew")
    p.add_argument("--background-hive", choices=["user", "system"], default="user", help="Where to create background menu")
    p.add_argument("--keep-files", action="store_true", help="When uninstalling, keep installed files")
    args = p.parse_args()

    install_dir = Path(args.path) if args.path else None

    if args.action == "install":
        ok, msg = install(install_dir=install_dir, apply_registry=not args.no_registry,
                          shellnew_hive=args.shellnew_hive, background_hive=args.background_hive)
        print(msg)
        return 0 if ok else 1
    if args.action == "uninstall":
        ok, msg = uninstall(install_dir=install_dir, remove_files=not args.keep_files, remove_registry=not args.no_registry)
        print(msg)
        return 0 if ok else 1
    if args.action == "status":
        print(status(install_dir=install_dir))
        return 0

if __name__ == "__main__":
    raise SystemExit(_cli())
