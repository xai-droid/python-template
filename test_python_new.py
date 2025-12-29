import os
import subprocess

print("=== Python Neu-Menü Test (automatisch) ===\n")

# --- Skript- und Template-Pfade ---
script_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(script_dir, "templates")
template_file = os.path.join(templates_dir, "NeuePythonDatei.py")
empty_file = os.path.join(templates_dir, "LeerePythonDatei.py")
batch_file = os.path.join(script_dir, "create_python_new.bat")

# --- 1. Prüfen Templates ---
print("1. Prüfe Templates...")
for f, name in [(template_file, "Template-Datei"), (empty_file, "Leere Datei"), (batch_file, "Batch-Wrapper")]:
    if os.path.exists(f):
        print(f"[OK] {name} gefunden: {f}")
    else:
        print(f"[FEHLER] {name} fehlt: {f}")

# --- 2. Automatisches Erstellen Template ---
print("\n2. Test: Template-Datei erstellen...")
subprocess.run(
    ["python", os.path.join(script_dir, "create_python_new.py"), os.getcwd(), "t"],
    text=True,
    shell=True
)

# --- 3. Automatisches Erstellen Leere Datei ---
print("\n3. Test: Leere Datei erstellen...")
subprocess.run(
    ["python", os.path.join(script_dir, "create_python_new.py"), os.getcwd(), "l"],
    text=True,
    shell=True
)

# --- 4. Prüfen ob Dateien erstellt wurden ---
template_created = any(f.startswith("NeuePythonDatei_Template") and f.endswith(".py") for f in os.listdir(os.getcwd()))
empty_created = any(f.startswith("NeuePythonDatei_Leer") and f.endswith(".py") for f in os.listdir(os.getcwd()))

print("\n4. Ergebnisprüfung:")
print(f"Template-Datei erstellt: {'Ja' if template_created else 'Nein'}")
print(f"Leere Datei erstellt: {'Ja' if empty_created else 'Nein'}")

print("\n=== Test abgeschlossen ===")
