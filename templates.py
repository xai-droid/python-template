import os
import shutil

user_templates = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Templates")
os.makedirs(user_templates, exist_ok=True)

template_file = os.path.join(user_templates, "NeuePythonDatei.py")
template_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

def main():
    pass

if __name__ == "__main__":
    main()
"""

with open(template_file, "w", encoding="utf-8") as f:
    f.write(template_content)

print(f"Template-Datei erstellt: {template_file}")
