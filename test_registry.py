import winreg

def check_key(root, path):
    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
        return key
    except FileNotFoundError:
        return None

def check_background_entry():
    print("=== Hintergrund-Kontextmenü prüfen ===")
    possible = [
        r"Software\Classes\Directory\Background\shell\NeuePythonDatei_Hintergrund",
        r"Software\Classes\Directory\Background\shell\NeuePythonDatei",
    ]
    key = None
    found_path = None
    for p in possible:
        key = check_key(winreg.HKEY_CURRENT_USER, p)
        if key:
            found_path = p
            break
    if not key:
        print("[FEHLER] Hintergrund-Menüeintrag NICHT gefunden (checked candidate names).")
        return
    print(f"[OK] Hintergrund-Menüeintrag gefunden: {found_path}")
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
    key = check_key(winreg.HKEY_CLASSES_ROOT, key_path) or check_key(winreg.HKEY_CURRENT_USER, r"Software\Classes\.py\ShellNew")
    if not key:
        print("[FEHLER] .py Neu-Menü Eintrag NICHT gefunden (HKCR or HKCU checked).")
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
