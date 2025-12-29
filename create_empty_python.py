import os
import sys
import shutil

empty_file = r"C:\Users\alexh\AppData\Roaming\Microsoft\Windows\Templates\LeerePythonDatei.py"

target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

i = 1
while True:
    target_file = os.path.join(target_dir, f"NeuePythonDatei_Leer{i}.py")
    if not os.path.exists(target_file):
        break
    i += 1

shutil.copy(empty_file, target_file)
print(f"Leere Python-Datei erstellt: {target_file}")
