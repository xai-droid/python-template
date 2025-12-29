import os

# 1. Windows Templates-Ordner
templates_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Templates")
os.makedirs(templates_dir, exist_ok=True)

# 2. Template-Datei erstellen
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

# 3. Registry-Datei erstellen
reg_file = os.path.join(os.getcwd(), "python_3_14_2_neu.reg")

reg_lines = [
    "Windows Registry Editor Version 5.00\n",
    "; ===== Python 3.14.2 Rechtsklick 'Neu' mit Template =====\n",
    
    # .py-Dateiendung
    "[HKEY_CLASSES_ROOT\\.py]",
    '@="Python.File"',
    '"Content Type"="text/plain"\n',
    
    # ShellNew mit FileName auf Template-Datei
    "[HKEY_CLASSES_ROOT\\.py\\ShellNew]",
    f'"FileName"="{template_file_name}"\n',
    
    # Icon
    "[HKEY_CLASSES_ROOT\\Python.File\\DefaultIcon]",
    '@="C:\\\\Windows\\\\py.exe,0"\n',
    
    # Rechtsklick-Menü für Python 3.14.2
    "[HKEY_CLASSES_ROOT\\Python.File\\shell\\RunWithPython3142]",
    '@="Mit Python 3.14.2 ausführen"\n',
    "[HKEY_CLASSES_ROOT\\Python.File\\shell\\RunWithPython3142\\command]",
    '@="\"C:\\\\Windows\\\\py.exe\" -3.14 \"%1\""\n'
]

with open(reg_file, "w", encoding="utf-16") as f:
    for line in reg_lines:
        f.write(line + "\n")

print(f"Registry-Datei erstellt: {reg_file}")
print("Doppelklick auf die .reg-Datei, um das 'Neu'-Menü zu aktualisieren.")
print("Wenn das Menü noch nicht sichtbar ist: Windows Explorer neu starten (Task-Manager → Windows-Explorer → Neu starten).")
