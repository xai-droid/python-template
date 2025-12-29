import os
import sys
import shutil

def get_templates_dir():
    return os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft",
        "Windows",
        "Templates"
    )

def main():
    templates_dir = get_templates_dir()
    empty_template = os.path.join(templates_dir, "LeerePythonDatei.py")

    if not os.path.exists(empty_template):
        raise FileNotFoundError("LeerePythonDatei.py nicht im Templates-Ordner gefunden")

    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    index = 1
    while True:
        target_file = os.path.join(
            target_dir,
            f"NeuePythonDatei_Leer{index}.py"
        )
        if not os.path.exists(target_file):
            break
        index += 1

    shutil.copy(empty_template, target_file)

if __name__ == "__main__":
    main()
