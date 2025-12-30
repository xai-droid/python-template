import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from typing import Optional, Dict, Any

import registry

APP_TITLE = "py-new-file — Registry"

# minimal tooltip helper (same behavior as gui.ToolTip)
class ToolTip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self._win: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hide()

    def _schedule(self):
        self._unschedule()
        self._id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        if self._id:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _show(self):
        if self._win or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._win = tk.Toplevel(self.widget)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(self._win, text=self.text, relief="solid", padding=(6,4), background="#ffffe0")
        lbl.pack()
        self.widget.after(30000, self._hide)

    def _hide(self):
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None


class RegistryGUI(tk.Tk):
    """Simple GUI to view/edit the JSON-backed registry and manage shell entries."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("800x460")
        self.minsize(640, 360)
        self._setup_style()
        self._create_widgets()
        self._load_keys()

    def _setup_style(self):
        default_font = ("Segoe UI", 10)
        self.option_add("*Font", default_font)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))

    def _create_widgets(self):
        main = ttk.Frame(self, padding=(10,10,10,10))
        main.pack(fill="both", expand=True)

        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # left: keys list
        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        ttk.Label(left, text="Registry keys", style="Header.TLabel").pack(anchor="w")
        self.key_list = tk.Listbox(left, width=30, activestyle="none", exportselection=False)
        self.key_list.pack(fill="both", expand=True, pady=(6,6))
        self.key_list.bind("<<ListboxSelect>>", lambda e: self._on_select())
        key_btns = ttk.Frame(left)
        key_btns.pack(fill="x")
        ttk.Button(key_btns, text="New", command=self._new_key).pack(side="left", padx=(0,6))
        ttk.Button(key_btns, text="Delete", command=self._delete_key).pack(side="left", padx=(6,6))
        ttk.Button(key_btns, text="Refresh", command=self._load_keys).pack(side="left", padx=(6,0))

        # right: editor and shell actions
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)
        ttk.Label(right, text="Key / Value editor", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(right, text="Key:").grid(row=1, column=0, sticky="e", padx=6, pady=(8,4))
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(right, textvariable=self.key_var)
        self.key_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=(8,4))

        ttk.Label(right, text="Value (JSON):").grid(row=2, column=0, sticky="ne", padx=6)
        self.value_text = tk.Text(right, height=10, wrap="word")
        self.value_text.grid(row=2, column=1, sticky="nsew", padx=6)
        # small hint
        ttk.Label(right, text="Enter JSON-serializable value (string, number, dict, list)").grid(row=3, column=1, sticky="w", padx=6, pady=(4,6))

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=4, column=1, sticky="e", pady=(6,0))
        self.save_btn = ttk.Button(btn_frame, text="Save", command=self._save_key)
        self.save_btn.pack(side="right", padx=(6,0))
        ToolTip(self.save_btn, "Save the key and value to the registry file.")
        self.discard_btn = ttk.Button(btn_frame, text="Discard", command=self._on_select)
        self.discard_btn.pack(side="right", padx=(6,0))
        ToolTip(self.discard_btn, "Discard unsaved edits and reload selected value.")

        # shell integration actions
        shell_frame = ttk.LabelFrame(right, text="Windows shell / ShellNew")
        shell_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10,0), padx=(0,0))
        shell_frame.columnconfigure(1, weight=1)

        # Background entry row: status + hive selector + actions
        ttk.Label(shell_frame, text="Background entry:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.bg_status_lbl = ttk.Label(shell_frame, text="Unknown", width=30)
        self.bg_status_lbl.grid(row=0, column=1, sticky="w", padx=6)
        self.bg_hive_box = ttk.Combobox(shell_frame, values=["user", "system"], width=10, state="readonly")
        self.bg_hive_box.set("user")
        self.bg_hive_box.grid(row=0, column=2, sticky="w", padx=6)
        ttk.Button(shell_frame, text="Create/Update", command=self._create_background).grid(row=0, column=3, sticky="w", padx=6, pady=4)
        ttk.Button(shell_frame, text="Remove", command=self._remove_background).grid(row=0, column=4, sticky="w", padx=6, pady=4)

        # Separator
        ttk.Separator(shell_frame, orient="horizontal").grid(row=1, column=0, columnspan=5, sticky="ew", pady=(6,6))

        # ShellNew (.py) row: show filename and hive + actions
        ttk.Label(shell_frame, text=".py ShellNew:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.shellnew_file_var = tk.StringVar()
        self.shellnew_file_entry = ttk.Entry(shell_frame, textvariable=self.shellnew_file_var)
        self.shellnew_file_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=6)
        self.shellnew_hive_box = ttk.Combobox(shell_frame, values=["system", "user"], width=10, state="readonly")
        self.shellnew_hive_box.set("system")
        self.shellnew_hive_box.grid(row=2, column=3, sticky="w", padx=6)
        ttk.Button(shell_frame, text="Save", command=self._create_shellnew).grid(row=2, column=4, sticky="w", padx=6)
        ttk.Button(shell_frame, text="Remove", command=self._remove_shellnew).grid(row=2, column=5, sticky="w", padx=6)

        # Refresh button to re-check actual registry state (and show where values live)
        ttk.Button(shell_frame, text="Refresh statuses", command=self._load_shell_status).grid(row=3, column=0, sticky="w", padx=6, pady=(8,4))
        ToolTip(shell_frame, "Refresh the detected state for Background entry and .py ShellNew.")
        # Populate status on start
        self.after(150, self._load_shell_status)

        # status bar
        self.status = ttk.Label(self, text="Ready", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0,10))

    def _load_keys(self):
        self.key_list.delete(0, "end")
        reg = registry.load_registry()
        for k in sorted(reg.keys()):
            self.key_list.insert("end", k)
        self.status.config(text=f"Loaded {len(reg)} keys")

    def _on_select(self):
        sel = self.key_list.curselection()
        if not sel:
            self.key_var.set("")
            self.value_text.delete("1.0", "end")
            return
        key = self.key_list.get(sel[0])
        val = registry.get(key)
        self.key_var.set(key)
        # pretty-print JSON value if possible
        import json
        try:
            txt = json.dumps(val, indent=2, ensure_ascii=False)
        except Exception:
            txt = str(val)
        self.value_text.delete("1.0", "end")
        self.value_text.insert("1.0", txt)
        self.status.config(text=f"Selected {key}")

    def _save_key(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning(APP_TITLE, "Enter a key name.")
            return
        raw = self.value_text.get("1.0", "end").strip()
        if not raw:
            # empty -> delete key after confirmation
            if messagebox.askyesno(APP_TITLE, f"Value is empty. Delete key '{key}'?"):
                ok = registry.delete(key)
                if ok:
                    self._load_keys()
                    self.status.config(text=f"Deleted key {key}")
                else:
                    self.status.config(text=f"Key {key} did not exist")
            return
        # parse JSON if possible, otherwise store as string
        import json
        try:
            val = json.loads(raw)
        except Exception:
            val = raw
        registry.set(key, val)
        self._load_keys()
        # select saved key
        try:
            idx = list(self.key_list.get(0, "end")).index(key)
            self.key_list.selection_clear(0, "end")
            self.key_list.selection_set(idx)
            self.key_list.see(idx)
        except ValueError:
            pass
        self.status.config(text=f"Saved {key}")

    def _delete_key(self):
        sel = self.key_list.curselection()
        if not sel:
            messagebox.showinfo(APP_TITLE, "Select a key to delete.")
            return
        key = self.key_list.get(sel[0])
        if not messagebox.askyesno(APP_TITLE, f"Delete key '{key}'?"):
            return
        ok = registry.delete(key)
        if ok:
            self._load_keys()
            self.value_text.delete("1.0", "end")
            self.key_var.set("")
            self.status.config(text=f"Deleted {key}")
        else:
            self.status.config(text=f"Key {key} not found")

    def _new_key(self):
        """Create a new registry key entry (prepare editor)."""
        name = simpledialog.askstring(APP_TITLE, "New key name:")
        if not name:
            return
        name = name.strip()
        if not name:
            return
        # warn if it exists
        if registry.get(name) is not None:
            messagebox.showwarning(APP_TITLE, "A key with that name already exists.")
            return
        # prepare editor for new key (unsaved)
        self.key_var.set(name)
        self.value_text.delete("1.0", "end")
        self.key_entry.focus_set()
        self.status.config(text=f"New key {name} (unsaved)")

    # shell / shellnew actions

    def _check_background(self):
        ok, hive = registry.check_entry_background()
        if ok:
            messagebox.showinfo(APP_TITLE, f"Background entry present ({hive})")
            self.bg_status_lbl.config(text=f"Present ({hive})")
            self.status.config(text=f"Background: present ({hive})")
        else:
            messagebox.showinfo(APP_TITLE, "Background entry not found")
            self.bg_status_lbl.config(text="Not present")
            self.status.config(text="Background: absent")

    def _create_background(self):
        hive = self.bg_hive_box.get() or "user"
        ok, msg = registry.create_entry_background(hive=hive)
        if ok:
            messagebox.showinfo(APP_TITLE, f"Created/Updated background entry ({hive})")
        else:
            messagebox.showerror(APP_TITLE, f"Failed to create background entry ({hive}):\n{msg}")
        self.status.config(text=f"Create background ({hive}): {msg}")
        self._load_shell_status()

    def _remove_background(self):
        hive = self.bg_hive_box.get() or "user"
        if not messagebox.askyesno(APP_TITLE, f"Remove background entry from {hive}?"):
            return
        ok, msg = registry.remove_entry_background(hive=hive)
        if ok:
            messagebox.showinfo(APP_TITLE, f"Background entry removed ({hive})")
        else:
            messagebox.showerror(APP_TITLE, f"Failed to remove background entry ({hive}):\n{msg}")
        self.status.config(text=f"Remove background ({hive}): {msg}")
        self._load_shell_status()

    def _check_shellnew(self):
        ok, hive = registry.check_shellnew_py()
        if ok:
            messagebox.showinfo(APP_TITLE, f".py ShellNew present ({hive})")
            self.status.config(text=f".py ShellNew: present ({hive})")
        else:
            messagebox.showinfo(APP_TITLE, ".py ShellNew not found")
            self.status.config(text=".py ShellNew: absent")

    def _create_shellnew(self):
        name = (self.shellnew_file_var.get() or "").strip()
        if not name:
            messagebox.showwarning(APP_TITLE, "Enter a valid FileName to register (e.g. NeuePythonDatei.py)")
            return
        hive = self.shellnew_hive_box.get() or "system"
        ok, msg = registry.create_shellnew_py(name, hive=hive)
        if ok:
            messagebox.showinfo(APP_TITLE, f".py ShellNew created/updated ({hive})")
        else:
            messagebox.showerror(APP_TITLE, f"Failed to create .py ShellNew ({hive}):\n{msg}")
        self.status.config(text=f"Create ShellNew ({hive}): {msg}")
        self._load_shell_status()

    def _remove_shellnew(self):
        hive = self.shellnew_hive_box.get() or "system"
        if not messagebox.askyesno(APP_TITLE, f"Remove .py ShellNew from {hive}?"):
            return
        ok, msg = registry.remove_shellnew_py(hive=hive)
        if ok:
            messagebox.showinfo(APP_TITLE, f".py ShellNew removed ({hive})")
        else:
            messagebox.showerror(APP_TITLE, f"Failed to remove .py ShellNew ({hive}):\n{msg}")
        self.status.config(text=f"Remove ShellNew ({hive}): {msg}")
        self._load_shell_status()

    def _load_shell_status(self):
        """Refresh background and ShellNew status and populate UI controls."""
        # Background
        try:
            ok, hive = registry.check_entry_background()
        except Exception:
            ok, hive = False, None
        if ok:
            self.bg_status_lbl.config(text=f"Present ({hive})")
            self.bg_hive_box.set("user" if hive == "HKCU" else "system")
        else:
            self.bg_status_lbl.config(text="Not present")

        # ShellNew existence + filename (try reading directly via winreg for filename)
        try:
            ok2, hive2 = registry.check_shellnew_py()
        except Exception:
            ok2, hive2 = False, None
        if ok2:
            # attempt to read FileName value
            fname = None
            try:
                import winreg  # type: ignore
                # check HKCR first
                if hive2 == "HKCR":
                    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r".py\ShellNew")
                    fname, _ = winreg.QueryValueEx(key, "FileName")
                    winreg.CloseKey(key)
                    self.shellnew_hive_box.set("system")
                else:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.py\ShellNew")
                    fname, _ = winreg.QueryValueEx(key, "FileName")
                    winreg.CloseKey(key)
                    self.shellnew_hive_box.set("user")
            except Exception:
                fname = ""
            self.shellnew_file_var.set(fname or "")
            self.status.config(text=f".py ShellNew: present ({hive2})")
        else:
            self.shellnew_file_var.set("")
            self.status.config(text=".py ShellNew: absent")


def main():
    app = RegistryGUI()
    app.mainloop()


if __name__ == "__main__":
    main()