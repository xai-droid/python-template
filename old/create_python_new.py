import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import subprocess
import random
import shutil

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

CACHE_FILE = Path.home() / ".python_new_cache"

# --- Helper für zufällige Namen ---
def random_name():
    syllables = ["ka", "li", "mo", "ra", "zu", "el", "fi", "na", "to", "va", "re", "shi", "da"]
    return "".join(random.choice(syllables).capitalize() for _ in range(random.randint(2,4))) + ".py"

# --- Registry Update Funktion ---
def update_registry(template_name):
    import winreg
    key_path = r"Software\Classes\Directory\Background\shell\NeuePythonDatei\command"
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            script_path = Path(__file__).resolve()
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}" "%V"')
    except Exception as e:
        messagebox.showerror("Registry Fehler", str(e))

# --- GUI ---
class PythonNewGUI(tk.Tk):
    def __init__(self, target_dir):
        super().__init__()
        self.title("Neue Python-Datei")
        self.geometry("800x600")
        self.minsize(600,400)
        self.target_dir = Path(target_dir)
        self.template_var = tk.StringVar()
        self.open_vscode = tk.BooleanVar(value=False)
        self.as_template = tk.BooleanVar(value=False)

        self.vscode_path = shutil.which("code")
        self._build_ui()
        self._load_templates()
        self._load_cache()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Dateiname:").grid(row=0,column=0,sticky="w")
        self.filename_entry = ttk.Entry(frm)
        self.filename_entry.grid(row=0,column=1,sticky="ew",columnspan=2,pady=5)

        ttk.Button(frm, text="Random Name", command=self._set_random_name).grid(row=0,column=3,sticky="w",padx=5)

        ttk.Label(frm, text="Template wählen:").grid(row=1,column=0,sticky="w")
        self.template_combo = ttk.Combobox(frm, textvariable=self.template_var, state="readonly")
        self.template_combo.grid(row=1,column=1,sticky="ew",columnspan=2)
        self.template_combo.bind("<<ComboboxSelected>>", lambda e: self._load_template_content())

        ttk.Checkbutton(frm, text="VS Code öffnen", variable=self.open_vscode).grid(row=2,column=0,sticky="w")
        ttk.Checkbutton(frm, text="Als Template speichern", variable=self.as_template).grid(row=2,column=1,sticky="w")

        self.text = ScrolledText(frm, wrap="none", undo=True, bg="#1e1e1e", fg="#d4d4d4",
                                 insertbackground="white", selectbackground="#264f78")
        self.text.grid(row=3,column=0,columnspan=4,sticky="nsew",pady=10)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4,column=0,columnspan=4,sticky="ew")
        ttk.Button(btn_frame, text="Erstellen", command=self.create_file).pack(side="right",padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.destroy).pack(side="right",padx=5)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

    def _set_random_name(self):
        self.filename_entry.delete(0,"end")
        self.filename_entry.insert(0, random_name())

    def _load_templates(self):
        files = [f.name for f in TEMPLATES_DIR.glob("*.py")]
        self.template_combo["values"] = files
        if files:
            self.template_var.set(files[0])
            self._load_template_content()

    def _load_template_content(self):
        name = self.template_var.get()
        if not name:
            self.text.delete("1.0","end")
            return
        path = TEMPLATES_DIR / name
        if path.exists():
            self.text.delete("1.0","end")
            self.text.insert("1.0", path.read_text(encoding="utf-8"))

    def _load_cache(self):
        if CACHE_FILE.exists():
            self.text.insert("1.0", CACHE_FILE.read_text(encoding="utf-8"))

    def _save_cache(self):
        CACHE_FILE.write_text(self.text.get("1.0","end-1c"), encoding="utf-8")

    def create_file(self):
        try:
            name = self.filename_entry.get().strip()
            if not name.lower().endswith(".py"):
                name += ".py"
            target_path = self.target_dir / name

            if target_path.exists():
                overwrite = messagebox.askyesno("Datei existiert", f"'{name}' existiert bereits. Überschreiben?")
                if not overwrite:
                    self.text.delete("1.0","end")
                    self.text.insert("1.0", target_path.read_text(encoding="utf-8"))
                    messagebox.showinfo("Info", f"Datei '{name}' geladen")
                    return

            content = self.text.get("1.0","end-1c")
            target_path.write_text(content, encoding="utf-8")
            self._save_cache()

            if self.open_vscode.get() and self.vscode_path:
                subprocess.Popen([self.vscode_path, str(target_path)])

            if self.as_template.get():
                template_path = TEMPLATES_DIR / name
                template_path.write_text(content, encoding="utf-8")
                self._load_templates()
                update_registry(name)
                messagebox.showinfo("Template", f"Template gespeichert: {name}")

            messagebox.showinfo("Erfolg", f"Datei erstellt: {name}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

def main():
    target_dir = sys.argv[1] if len(sys.argv)>1 else os.getcwd()
    if not os.path.isdir(target_dir):
        messagebox.showerror("Fehler", f"Ungültiges Zielverzeichnis:\n{target_dir}")
        return
    app = PythonNewGUI(target_dir)
    app.mainloop()

if __name__ == "__main__":
    main()
