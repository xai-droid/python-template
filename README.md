# Python New File GUI

**Erstellt neue Python-Dateien über das Windows Explorer Kontextmenü.**

## Features
- Rechtsklick → „Neue Python-Datei erstellen…“ (Hintergrund & Neu-Menü)
- Dunkler Editor mit:
  - Aktuelle Zeile grün markiert
  - Vim-Style Navigation (`h/j/k/l`)
  - Syntax-Highlighting (Pygments, optional)
- Template-Editor: eigenen Inhalt bearbeiten und als Template speichern
- Optional VS Code öffnen
- Portabel: relative Pfade für BAT/Registry

## Installation
1. Ordnerstruktur:
   ```
   py-new-file/
   ├─ create_python_new.py
   ├─ create_python_new_gui.bat
   ├─ python_new_context.reg
   └─ templates/
       ├─ NeuePythonDatei.py
       └─ LeerePythonDatei.py
   ```
2. Doppelklick auf `python_new_context.reg`, um Neu-Menü & Hintergrundmenü einzurichten.
3. Rechtsklick im Explorer → „Neue Python-Datei erstellen…“ startet die GUI.

## Nutzung
- Wähle „Template“ oder „Leer“.
- Bearbeite Inhalt optional.
- Checkbox „Als Template speichern“, falls du es für zukünftige Dateien sichern willst.
- Optional VS Code öffnen.

## Hinweise
- Python muss im PATH sein.
- GUI startet ohne sichtbares CMD-Fenster.

