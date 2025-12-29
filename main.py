#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

# --- 1. Skriptordner ---
script_dir = os.getcwd()

# --- 2. Template-Datei ---
template_file = os.path.join(script_dir, "NeuePythonDatei.py")
if not os.path.exists(template_file):
    with open(template_file, "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

def main():
    pass

if __name__ == "__main__":
    main()
""")

# --- 3. Leere Datei ---
empty_file = os.path.join(script_dir, "LeerePythonDatei.py")
if not os.path.exists(empty_file):
    with open(empty_file, "w", encoding="utf-8") as f:
        f.write("# Leere Python-Datei\n")

# --- 4. Skript für Kontextmenü-Auswahl ---
script_file = os.path.join(script_dir, "create_python_new.py")
script_content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

script_dir = os.path.dirname(os.path.abspath(__file__))
template_file = os.path.join(script_dir, "NeuePythonDatei.py")
empty_file = os.path.join(script_dir, "LeerePythonDatei.py")

target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

root = tk.Tk()
root.withdraw()

choice = simpledialog.askstring("Neue Python-Datei", "Erstellen: template oder leer?", initialvalue="template")
if choice is None:
    sys.exit()
choice = choice.lower()
if choice not in ("template", "leer"):
    messagebox.showerror("Fehler", "Ungültige Auswahl. Bitte 'template' oder 'leer' eingeben.")
    sys.exit(1)

if choice == "template":
    src = template_file
    prefix = "NeuePythonDatei"
else:
    src = empty_file
    prefix = "NeuePythonDatei_Leer"

i = 1
while True:
    target_file = os.path.join(target_dir, f"{{prefix}}{{i}}.py")
    if not os.path.exists(target_file):
        break
    i += 1

shutil.copy(src, target_file)
messagebox.showinfo("Erfolg", f"{{choice.capitalize()}} Python-Datei erstellt:\\n{{target_file}}")
"""
with open(script_file, "w", encoding="utf-8") as f:
    f.write(script_content)

# --- 5. Registry-Datei für Kontextmenü ---
reg_file_context = os.path.join(script_dir, "python_new_context.reg")
script_path_escaped = script_file.replace("\\", "\\\\")
reg_content_context = f"""Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\NeuePythonDatei]
@="Neue Python-Datei erstellen..."
"Icon"="python.exe"

[HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\NeuePythonDatei\\command]
@="python \\"{script_path_escaped}\\" \\"%V\\""
"""
with open(reg_file_context, "w", encoding="utf-16") as f:
    f.write(reg_content_context)

# --- 6. Registry-Datei für ShellNew (Neu-Menü Template) ---
reg_file_new = os.path.join(script_dir, "python_template_restore.reg")
reg_content_new = f"""Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\\.py]
@="Python.File"
"Content Type"="text/plain"

[HKEY_CLASSES_ROOT\\.py\\ShellNew]
"FileName"="{os.path.basename(template_file)}"
"""
with open(reg_file_new, "w", encoding="utf-16") as f:
    f.write(reg_content_new)

# --- 7. Explorer neu starten ---
try:
    subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True)
    subprocess.run(["start", "explorer.exe"], shell=True, check=True)
except Exception as e:
    print(f"Fehler beim Neustart des Explorers: {e}")

print("Setup abgeschlossen!")
print(f"- Skript erstellt: {script_file}")
print(f"- Registry-Datei Kontextmenü: {reg_file_context}")
print(f"- Registry-Datei Neu-Menü Template: {reg_file_new}")
print("Menüeinträge sollten jetzt sichtbar sein.")
