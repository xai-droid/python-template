# Python Template – Windows New File Integration

**python-template** is a lightweight Python utility that integrates directly into the **Windows Explorer right-click menu** to create new Python files.  
It supports both **template-based file generation via a GUI** and **instant creation of empty Python files**.

The installation and system integration are handled via `setup_newfile.py`.

---

## Features

- Windows Explorer **right-click integration**
- Create Python files:
  - From **predefined templates** (GUI-based)
  - As a **completely empty `.py` file**
- Tkinter-based GUI for template selection
- Persistent configuration via JSON registry
- No third-party dependencies
- Pure Python (standard library only)

---

## How It Works

After installation:

1. Right-click inside any folder in Windows Explorer
2. Choose one of the new context menu entries:
   - **New → Python File (Template)**
   - **New → Python File (Empty)**
3. The selected action:
   - Opens a GUI to choose a template **or**
   - Instantly creates an empty `.py` file

---

## Installation

### Requirements

- Windows 10 or newer
- Python 3.8+

### Install Context Menu Integration

Run the setup script:

```bash
python setup_newfile.py
