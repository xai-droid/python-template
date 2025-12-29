import winreg

def check_key(root, path):
    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
        return key
    except FileNotFoundError:
        return None

def check_background_entry():
    print("=== Hintergrund-Kontextmenü prüfen ===")
    key_path = r"Software\Classes\Directory\Background\shell\NeuePythonDatei_Hintergrund"
    key = check_key(winreg.HKEY_CURRENT_USER, key_path)
    if not key:
        print("[FEHLER] Hintergrund-Menüeintrag NICHT gefunden.")
        return

    print("[OK] Hintergrund-Menüeintrag gefunden.")
    try:
        cmd_key = check_key(winreg.HKEY_CURRENT_USER, key_path + r"\command")
        if cmd_key:
            command, _ = winreg.QueryValueEx(cmd_key, "")
            print(f"Command: {command}")
        else:
            print("[FEHLER] command-Subkey fehlt!")
    except Exception as e:
        print(f"[FEHLER] Beim Auslesen des command-Schlüssels: {e}")

def check_new_py_entry():
    print("\n=== .py Neu-Menü prüfen ===")
    key_path = r".py\ShellNew"
    key = check_key(winreg.HKEY_CLASSES_ROOT, key_path)
    if not key:
        print("[FEHLER] .py Neu-Menü Eintrag NICHT gefunden.")
        return

    print("[OK] .py Neu-Menü Eintrag gefunden.")
    try:
        file_name, _ = winreg.QueryValueEx(key, "FileName")
        print(f"FileName: {file_name}")
    except FileNotFoundError:
        print("[FEHLER] FileName-Wert nicht gefunden!")

if __name__ == "__main__":
    check_background_entry()
    check_new_py_entry()
