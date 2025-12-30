import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import shutil

# Installationspfad automatisch erkennen
INSTALL_DIR = Path(__file__).parent
TEMPLATE_FILE = INSTALL_DIR / "templates" / "NeuePythonDatei.py"
EMPTY_FILE = INSTALL_DIR / "templates" / "LeerePythonDatei.py"

# Zielverzeichnis
TARGET_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
if not TARGET_DIR.exists():
    messagebox.showerror("Fehler", f"Zielverzeichnis existiert nicht:\n{TARGET_DIR}")
    sys.exit(1)

# --- GUI ---
root = tk.Tk()
root.title("Neue Python-Datei erstellen")
root.geometry("600x400")

# Dateiname
filename_var = tk.StringVar(value="neue_datei.py")
tk.Label(root, text="Dateiname:").pack(anchor="w", padx=10, pady=5)
filename_entry = tk.Entry(root, textvariable=filename_var)
filename_entry.pack(fill="x", padx=10)

# Auswahl Template / Leer
mode_var = tk.StringVar(value="template")
tk.Radiobutton(root, text="Template", variable=mode_var, value="template").pack(anchor="w", padx=10)
tk.Radiobutton(root, text="Leer", variable=mode_var, value="empty").pack(anchor="w", padx=10)

# Editor
editor = ScrolledText(root, wrap="none", height=15)
editor.pack(fill="both", expand=True, padx=10, pady=5)

# Template laden
def load_template():
    path = TEMPLATE_FILE if mode_var.get() == "template" else EMPTY_FILE
    if path.exists():
        editor.delete("1.0", "end")
        editor.insert("1.0", path.read_text(encoding="utf-8"))

load_template()
mode_var.trace_add("write", lambda *args: load_template())

# Datei erstellen
def create_file():
    name = filename_var.get().strip()
    if not name.endswith(".py"):
        name += ".py"
    target_file = TARGET_DIR / name

    if target_file.exists():
        if not messagebox.askyesno("Datei existiert", f"{name} existiert bereits. Überschreiben?"):
            return

    target_file.write_text(editor.get("1.0", "end-1c"), encoding="utf-8")
    messagebox.showinfo("Erfolg", f"Datei erstellt:\n{target_file}")
    root.destroy()

tk.Button(root, text="Erstellen", command=create_file).pack(side="right", padx=10, pady=5)
tk.Button(root, text="Abbrechen", command=root.destroy).pack(side="right", padx=5, pady=5)

root.mainloop()
