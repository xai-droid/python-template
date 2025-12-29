import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import traceback
import shutil

# --- Logging ---
LOG_FILE = Path(__file__).parent / "python_new_error.log"

def log_exception(e):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())

# --- Ordner und Dateien ---
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "templates"
TEMPLATE_DIR.mkdir(exist_ok=True)

TEMPLATE_FILE = TEMPLATE_DIR / "NeuePythonDatei.py"
EMPTY_FILE = TEMPLATE_DIR / "LeerePythonDatei.py"
CACHE_FILE = Path.home() / ".python_new_cache"

# --- Syntax Highlighting ---
try:
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

# --- VS Code Pfad automatisch finden ---
def find_vscode_exe():
    cli_path = shutil.which("code")
    if cli_path:
        return cli_path
    possible_paths = [
        os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft VS Code\Code.exe"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

VSCODE_PATH = find_vscode_exe()

class PythonNewGUI(tk.Tk):
    def __init__(self, target_dir):
        super().__init__()
        self.title("Neue Python-Datei")
        self.geometry("800x600")
        self.minsize(600, 400)

        self.target_dir = Path(target_dir)
        self.mode = tk.StringVar(value="template")
        self.open_vscode = tk.BooleanVar(value=False)
        self.as_template = tk.BooleanVar(value=False)

        self.vscode_available = VSCODE_PATH is not None

        self._build_ui()
        self._load_template()
        self._load_cache()
        self._highlight_current_line()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Dateiname:").grid(row=0, column=0, sticky="w")
        self.filename_entry = ttk.Entry(frm)
        self.filename_entry.insert(0, "neue_datei.py")
        self.filename_entry.grid(row=0, column=1, sticky="ew", pady=5, columnspan=2)

        ttk.Radiobutton(frm, text="Template", variable=self.mode,
                        value="template", command=self._load_template).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(frm, text="Leer", variable=self.mode,
                        value="empty", command=self._load_template).grid(row=1, column=1, sticky="w")

        self.cb_vscode = ttk.Checkbutton(frm, text="VS Code öffnen", variable=self.open_vscode)
        self.cb_vscode.grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Als Template speichern", variable=self.as_template).grid(row=2, column=1, sticky="w")

        if not self.vscode_available:
            self.cb_vscode.state(["disabled"])
            ttk.Label(frm, text="VS Code nicht gefunden", foreground="red").grid(row=2, column=2, sticky="w")

        # Dunkler Editor
        self.text = ScrolledText(frm, wrap="none", undo=True, bg="#1e1e1e", fg="#d4d4d4",
                                 insertbackground="white", selectbackground="#264f78")
        self.text.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=10)

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=3, sticky="ew")
        ttk.Button(btn_frame, text="Erstellen", command=self.create_file).pack(side="right", padx=5, pady=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.destroy).pack(side="right", padx=5, pady=5)

        # Grid configuration
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

        # Highlighting & Vim Style
        if PYGMENTS_AVAILABLE:
            self.text.bind("<KeyRelease>", lambda e: self._highlight_syntax())

        # Aktuelle Zeile markieren
        self.text.bind("<Button-1>", lambda e: self._highlight_current_line())
        self.text.bind("<KeyRelease>", lambda e: self._highlight_current_line())

        # Vim basic
        self.text.bind("h", lambda e: self._move_left(e))
        self.text.bind("l", lambda e: self._move_right(e))
        self.text.bind("j", lambda e: self._move_down(e))
        self.text.bind("k", lambda e: self._move_up(e))

        self.text.tag_configure("current_line", background="#006400")  # grün
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # --- Vim Navigation ---
    def _move_left(self, e): self.text.mark_set("insert", "insert-1c"); return "break"
    def _move_right(self, e): self.text.mark_set("insert", "insert+1c"); return "break"
    def _move_down(self, e): self.text.mark_set("insert", "insert+1l"); return "break"
    def _move_up(self, e): self.text.mark_set("insert", "insert-1l"); return "break"

    # --- Syntax Highlighting ---
    def _highlight_syntax(self):
        code = self.text.get("1.0", "end-1c")
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, "1.0", "end")
        for token, content in lex(code, PythonLexer()):
            if content.strip() == "":
                continue
            start_idx = self.text.search(content, "1.0", stopindex="end")
            if start_idx:
                end_idx = f"{start_idx}+{len(content)}c"
                self.text.tag_add(str(token), start_idx, end_idx)
                if token in Token.Keyword: self.text.tag_config(str(token), foreground="#569CD6")
                elif token in Token.Name.Builtin: self.text.tag_config(str(token), foreground="#4EC9B0")
                elif token in Token.Literal.String: self.text.tag_config(str(token), foreground="#CE9178")
                elif token in Token.Comment: self.text.tag_config(str(token), foreground="#6A9955")

    # --- Aktuelle Zeile ---
    def _highlight_current_line(self):
        self.text.tag_remove("current_line", "1.0", "end")
        self.text.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def _load_template(self):
        path = TEMPLATE_FILE if self.mode.get() == "template" else EMPTY_FILE
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self._highlight_syntax()

    def _load_cache(self):
        if CACHE_FILE.exists():
            self.text.insert("1.0", CACHE_FILE.read_text(encoding="utf-8"))

    def _save_cache(self):
        CACHE_FILE.write_text(self.text.get("1.0", "end-1c"), encoding="utf-8")

    def create_file(self):
        try:
            name = self.filename_entry.get().strip()
            if not name.lower().endswith(".py"):
                name += ".py"
            target_path = self.target_dir / name

            if target_path.exists():
                overwrite = messagebox.askyesno(
                    "Datei existiert",
                    f"'{target_path.name}' existiert bereits. Überschreiben?"
                )
                if not overwrite:
                    content = target_path.read_text(encoding="utf-8")
                    self.text.delete("1.0", "end")
                    self.text.insert("1.0", content)
                    self._highlight_syntax()
                    messagebox.showinfo("Info", f"Datei '{target_path.name}' geladen")
                    return

            content = self.text.get("1.0", "end-1c")
            target_path.write_text(content, encoding="utf-8")
            self._save_cache()

            if self.vscode_available and self.open_vscode.get():
                subprocess.Popen([VSCODE_PATH, str(target_path)])

            if self.as_template.get():
                TEMPLATE_FILE.write_text(content, encoding="utf-8")
                messagebox.showinfo("Template", f"Template gespeichert: {TEMPLATE_FILE}")

            messagebox.showinfo("Erfolg", f"Datei erstellt: {target_path}")
            self.destroy()
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Fehler", str(e))

    def _on_close(self):
        self._save_cache()
        self.destroy()

def main():
    try:
        target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
        if not os.path.isdir(target_dir):
            messagebox.showerror("Fehler", f"Ungültiges Zielverzeichnis:\n{target_dir}")
            return
        app = PythonNewGUI(target_dir)
        app.mainloop()
    except Exception as e:
        log_exception(e)

if __name__ == "__main__":
    main()
