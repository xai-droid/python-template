import os
import shutil

# --- 1. Windows Templates-Ordner ---
templates_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Templates")
os.makedirs(templates_dir, exist_ok=True)

# --- 2. Template-Datei ---
template_file_name = "NeuePythonDatei.py"
template_file_path = os.path.join(templates_dir, template_file_name)
template_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

def main():
    pass

if __name__ == "__main__":
    main()
"""
with open(template_file_path, "w", encoding="utf-8") as f:
    f.write(template_content)
print(f"Template-Datei erstellt: {template_file_path}")

# --- 3. Leere Python-Datei ---
empty_file_name = "LeerePythonDatei.py"
empty_file_path = os.path.join(templates_dir, empty_file_name)
empty_content = "# Leere Python-Datei\n"
with open(empty_file_path, "w", encoding="utf-8") as f:
    f.write(empty_content)
print(f"Leere Python-Datei erstellt: {empty_file_path}")

# --- 4. Hilfsskript für leere Datei ---
helper_script = os.path.join(os.getcwd(), "create_empty_python.py")
helper_content = f"""import os
import sys
import shutil

empty_file = r\"{empty_file_path}\"

target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

i = 1
while True:
    target_file = os.path.join(target_dir, f"NeuePythonDatei_Leer{{i}}.py")
    if not os.path.exists(target_file):
        break
    i += 1

shutil.copy(empty_file, target_file)
print(f"Leere Python-Datei erstellt: {{target_file}}")
"""
with open(helper_script, "w", encoding="utf-8") as f:
    f.write(helper_content)
print(f"Hilfsskript erstellt: {helper_script}")

# --- 5. Registry-Datei für .py Neu-Menü ---
reg_file_py = os.path.join(os.getcwd(), "python_template_restore.reg")
reg_lines_py = [
    "Windows Registry Editor Version 5.00\n",
    "; .py Neu-Menü wiederherstellen mit Template\n",
    "[HKEY_CLASSES_ROOT\\.py]",
    '@="Python.File"',
    '"Content Type"="text/plain"\n',
    "[HKEY_CLASSES_ROOT\\.py\\ShellNew]",
    f'"FileName"="{template_file_name}"'
]
with open(reg_file_py, "w", encoding="utf-16") as f:
    for line in reg_lines_py:
        f.write(line + "\n")
print(f"Registry-Datei für .py erstellt: {reg_file_py}")

# --- 6. Registry-Datei für Rechtsklick-Menü leere Datei ---
reg_file_empty = os.path.join(os.getcwd(), "python_empty_context.reg")
helper_script_path = helper_script.replace("\\", "\\\\")
reg_lines_empty = [
    "Windows Registry Editor Version 5.00\n",
    "; Kontextmenü: Neue Python-Datei (leer)\n",
    "[HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\NeuePythonDateiLeer]",
    '@="Neue Python-Datei (leer)"',
    f"[HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\NeuePythonDateiLeer\\command]",
    f'@="python \\"{helper_script_path}\\" \\"%V\\""'
]
with open(reg_file_empty, "w", encoding="utf-16") as f:
    for line in reg_lines_empty:
        f.write(line + "\n")
print(f"Registry-Datei für Kontextmenü (leere Datei) erstellt: {reg_file_empty}")

print("\nSetup fertig! Schritte:")
print("1. Doppelklick auf python_template_restore.reg → .py Neu-Menü wiederherstellen")
print("2. Doppelklick auf python_empty_context.reg → Rechtsklick-Menü für leere Datei aktivieren")
print("3. Windows Explorer neu starten, wenn Änderungen nicht sofort sichtbar sind")
