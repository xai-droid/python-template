# Python-Template-Repository Handbuch

Dieses Handbuch beschreibt die Struktur und den Zweck des Repositorys, das eine automatische Erstellung neuer Python-Dateien im Windows „Neu“-Kontextmenü ermöglicht.

---

## 1. Ziel des Projekts

- Beim Rechtsklick → Neu → Python-Datei wird automatisch eine **vorgefertigte Template-Datei** erstellt.
- Zusätzlich kann eine **leere Python-Datei** erstellt werden, z. B. für `__init__.py` oder leere Module.  
- Rechtsklick-Menü „Mit Python 3.14.2 ausführen“ erlaubt das direkte Ausführen jeder Datei.
- Windows Registry wird angepasst, um beide Optionen im Menü korrekt anzuzeigen.

---

## 2. Projektstruktur

```
python-template/
├─ NeuePythonDatei.py        # Template-Datei für neue Python-Dateien
├─ LeerePythonDatei.py        # Leere Python-Datei für __init__.py oder leere Module
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

### 3.2 `LeerePythonDatei.py`

Leere Python-Datei, z. B. für `__init__.py` oder leere Module:

```python
# Leere Python-Datei
```

- Kann im Kontextmenü „Neu → Python-Datei (leer)“ verwendet werden.
- Ermöglicht minimale Dateien ohne Template-Code.

---

### 3.3 `python_3_14_2_neu.reg`

Registry-Datei für das Windows-Rechtsklick-Menü:

- Fügt Eintrag **Template-Datei** unter `.py` im Neu-Menü hinzu.  
- Fügt Eintrag **Leere Python-Datei** unter eigener Extension `.pyempty` hinzu, damit beide Optionen sichtbar sind.  
- Beide Optionen haben eigene Icons und Rechtsklick-Menü „Mit Python 3.14.2 ausführen“.

> Hinweis: Die Datei muss per Doppelklick in die Registry importiert werden.

---

### 3.4 `README.md`

- Enthält dieses Handbuch.
- Dokumentiert die Repository-Struktur und Funktionsweise.

---

## 4. Nutzung

1. Template-Datei (`NeuePythonDatei.py`) und leere Datei (`LeerePythonDatei.py`) werden automatisch in den **Windows Templates-Ordner** gelegt.  
2. Registry-Datei (`python_3_14_2_neu.reg`) importieren.  
3. Rechtsklick → Neu → **Python-Datei (Template)** oder **Python-Datei (leer)** → erzeugt automatisch die gewünschte Datei.  
4. Rechtsklick auf die Python-Datei → „Mit Python 3.14.2 ausführen“ startet das Skript.

---

## 5. Vorteile

- Schnelles Erstellen von neuen Python-Dateien mit Template oder leerer Datei.  
- Einheitliches Setup für alle Projekte.  
- Leichte Erweiterbarkeit für weitere Versionen oder Vorlagen.

---

## 6. Visualisierung

```
Windows Templates-Ordner
├─ NeuePythonDatei.py      -> Template
└─ LeerePythonDatei.py     -> Leere Datei

Registry:
HKEY_CLASSES_ROOT
 └─ .py
     └─ ShellNew
         └─ FileName = NeuePythonDatei.py
 └─ .pyempty
     └─ ShellNew
         └─ FileName = LeerePythonDatei.py
 └─ Python.TemplateFile
     └─ shell
         └─ RunWithPython3142
 └─ Python.EmptyFile
     └─ shell
         └─ RunWithPython3142
```

---

> Dieses Handbuch beschreibt nur die **lokale Repository-Struktur** und die Nutzung der enthaltenen Dateien. Git- oder Remote-Operationen sind hier nicht Teil des Handbuchs.

