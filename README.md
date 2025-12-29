# Python Neu-Menü Setup

Dieses Setup sorgt dafür, dass Windows im Rechtsklick-Menü Python-Dateien schnell erstellt:

## Features

- **Neu → Python-Datei**: Erstellt automatisch eine **Template-Datei**.
- **Rechtsklick → Hintergrund → Neue Python-Datei erstellen**: Optional Dialog für **Template oder leere Datei**.
- **Benutzer-spezifisch**: Alle Änderungen werden in `HKCU` gespeichert.

## Installation

1. Doppelklick auf `install_template.bat`:
   - Kopiert das Template nach `%APPDATA%\Microsoft\Windows\Templates`.
   - Repariert das „Neu-Menü“.
   - Startet den Explorer neu.

## Deinstallation

1. Doppelklick auf `uninstall.bat`:
   - Entfernt alle Registry-Einträge für „Neu → Python-Datei“ und Kontextmenüeinträge.
   - Löscht die Template-Datei.
   - Startet den Explorer neu.

## Hinweis

- Keine Admin-Rechte nötig, alles unter `HKCU`.
- Explorer muss neu gestartet werden, damit Änderungen sichtbar sind.
