# Python-Template-Repository Handbuch

Dieses Handbuch beschreibt die Struktur und den Zweck des Repositorys, das eine automatische Erstellung neuer Python-Dateien im Windows „Neu“-Kontextmenü ermöglicht.

---

## 1. Ziel des Projekts

- Beim Rechtsklick → Neu → Python-Datei wird automatisch eine **vorgefertigte Template-Datei** erstellt.
- Zusätzlich gibt es einen Rechtsklick-Eintrag „Mit Python 3.14.2 ausführen“, um die Datei direkt auszuführen.
- Windows Registry wird angepasst, um das Menü korrekt einzubinden.

---

## 2. Projektstruktur

```
python-template/
├─ NeuePythonDatei.py        # Template-Datei für neue Python-Dateien
├─ python_3_14_2_neu.reg     # Registry-Datei für Rechtsklick-Menü
├─ README.md                  # Dieses Handbuch
└─ ggf. weitere Hilfsdateien  # z.B. Skripte zum Erzeugen der Registry
```

---

## 3. Dateien im Detail

### 3.1 `NeuePythonDatei.py`

Template für neue Python-Dateien:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

def main():
    pass

if __name__ == "__main__":
    main()
```

- Wird automatisch in den **Windows Templates-Ordner** kopiert.
- Dient als Ausgangspunkt für neue Python-Skripte.

---

### 3.2 `python_3_14_2_neu.reg`

Registry-Datei für das Windows-Rechtsklick-Menü:

- Fügt Eintrag „Python-Datei“ im **Neu-Menü** hinzu.
- Bindet die Template-Datei ein (`FileName` auf `NeuePythonDatei.py`).
- Fügt Rechtsklick-Menü „Mit Python 3.14.2 ausführen“ hinzu.
- Icon für `.py`-Dateien wird auf `py.exe` gesetzt.

> Hinweis: Die Datei muss per Doppelklick in die Registry importiert werden.

---

### 3.3 `README.md`

- Enthält dieses Handbuch.
- Dokumentiert die Repository-Struktur und Funktionsweise.

---

## 4. Nutzung

1. Template-Datei wird automatisch in den **Windows Templates-Ordner** gelegt.  
2. Registry-Datei (`python_3_14_2_neu.reg`) importieren.  
3. Rechtsklick → Neu → Python-Datei → erzeugt automatisch das Template.  
4. Rechtsklick auf die Python-Datei → „Mit Python 3.14.2 ausführen“ startet das Skript.

---

## 5. Vorteile

- Schnelles Erstellen von neuen Python-Dateien mit Template.  
- Einheitliches Setup für alle Projekte.  
- Leichte Erweiterbarkeit für weitere Versionen oder Vorlagen.

---

## 6. Visualisierung (optional)

```
Windows Templates-Ordner
└─ NeuePythonDatei.py

Registry:
HKEY_CLASSES_ROOT
 └─ .py
     └─ ShellNew
         └─ FileName = NeuePythonDatei.py
 └─ Python.File
     └─ shell
         └─ RunWithPython3142
```

---

> Dieses Handbuch beschreibt nur die **lokale Repository-Struktur** und die Nutzung der enthaltenen Dateien. Git- oder Remote-Operationen sind hier nicht Teil des Handbuchs.

