import json
import os
from pathlib import Path
from string import Template
from typing import Dict, Optional, Tuple, Any
import uuid
import time


def random_name(prefix: str = "template") -> str:
    """Return a short unique template file name (with .py)."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}.py"


class TemplatesManager:
    def __init__(self, templates_dir: Path):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._meta_file = self.templates_dir / "templates.json"
        self._meta: Dict[str, Dict[str, Any]] = {}
        self._load_meta()
        self._ensure_default_templates()

    def _load_meta(self) -> None:
        if not self._meta_file.exists():
            self._meta = {}
            return
        try:
            raw = self._meta_file.read_text(encoding="utf-8")
            self._meta = json.loads(raw) or {}
        except Exception:
            # corrupted -> reset metadata
            self._meta = {}

    def _save_meta(self) -> None:
        tmp = str(self._meta_file) + ".tmp"
        os.makedirs(os.path.dirname(str(self._meta_file)), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._meta, f, indent=2, ensure_ascii=False)
        os.replace(tmp, str(self._meta_file))

    def _sanitize_name(self, name: str) -> str:
        base = os.path.basename(name)
        if not base.endswith(".py"):
            base = base + ".py"
        return base

    def _ensure_default_templates(self):
        # Provide at least one starter template if none exist.
        if any(self.list_templates()):
            return
        starter = (
            "#!/usr/bin/env python3\n"
            '"""Starter template: ${description}"""\n\n'
            "def main():\n"
            "    print('Hello from ${name}')\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )
        self.save_template("starter.py", starter, metadata={"description": "Simple starter script", "vars": ["name"]})
        # demo variables template
        demo = (
            "#!/usr/bin/env python3\n"
            '"""Demo template: shows variable substitution using ${var} placeholders"""\n\n'
            "# Name: ${name}\n"
            "# Description: ${description}\n"
            "# Author: ${author}\n"
            "# License: ${license}\n"
            "# Created: ${created_date}\n\n"
            "def main():\n"
            "    print('Project: ${name}')\n"
            "    print('Description: ${description}')\n"
            "    print('Author: ${author}')\n"
            "    print('License: ${license}')\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )
        self.save_template(
            "demo_variables.py",
            demo,
            metadata={
                "description": "Demonstrates template variables and usage of ${key} placeholders",
                "vars": ["name", "description", "author", "license", "created_date"],
            },
        )

    def list_templates(self) -> list:
        out = []
        for p in sorted(self.templates_dir.iterdir()):
            if p.is_file() and p.name.endswith(".py"):
                out.append(p.name)
        return out

    def create_template(self, name: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        name = self._sanitize_name(name)
        path = self.templates_dir / name
        if path.exists():
            raise FileExistsError(name)
        path.write_text(content, encoding="utf-8")
        self._meta[name] = metadata or {}
        self._save_meta()

    def save_template(self, name: str, content: str, metadata: Optional[Dict[str, Any]] = None, overwrite: bool = True) -> None:
        name = self._sanitize_name(name)
        path = self.templates_dir / name
        if path.exists() and not overwrite:
            raise FileExistsError(name)
        path.write_text(content, encoding="utf-8")
        if metadata is not None:
            self._meta[name] = metadata
        else:
            # preserve existing meta if any
            self._meta.setdefault(name, {})
        self._save_meta()

    def load_template(self, name: str, with_meta: bool = False) -> Any:
        name = self._sanitize_name(name)
        path = self.templates_dir / name
        if not path.exists():
            if with_meta:
                return "", self._meta.get(name, {})
            return ""
        content = path.read_text(encoding="utf-8")
        if with_meta:
            return content, self._meta.get(name, {})
        return content

    def get_metadata(self, name: str) -> Dict[str, Any]:
        name = self._sanitize_name(name)
        return self._meta.get(name, {})

    def delete_template(self, name: str) -> bool:
        name = self._sanitize_name(name)
        path = self.templates_dir / name
        removed = False
        if path.exists():
            path.unlink()
            removed = True
        if name in self._meta:
            del self._meta[name]
            self._save_meta()
        return removed

    def rename_template(self, old: str, new: str) -> None:
        oldn = self._sanitize_name(old)
        newn = self._sanitize_name(new)
        oldp = self.templates_dir / oldn
        newp = self.templates_dir / newn
        if not oldp.exists():
            raise FileNotFoundError(oldn)
        if newp.exists():
            raise FileExistsError(newn)
        oldp.replace(newp)
        # move metadata
        if oldn in self._meta:
            self._meta[newn] = self._meta.pop(oldn)
            self._save_meta()

    def render_template(self, name: str, vars: Optional[Dict[str, Any]] = None) -> str:
        name = self._sanitize_name(name)
        content = self.load_template(name)
        if not content:
            return ""
        # prepare vars as strings
        vars = {k: ("" if v is None else str(v)) for k, v in (vars or {}).items()}
        try:
            # first expand nested references inside variable values
            for _ in range(10):
                changed = False
                for k, v in list(vars.items()):
                    new_v = Template(v).safe_substitute(vars)
                    if new_v != v:
                        vars[k] = new_v
                        changed = True
                if not changed:
                    break
            # iterative content substitution
            current = content
            for _ in range(10):
                new = Template(current).safe_substitute(vars)
                if new == current:
                    break
                current = new
            return current
        except Exception:
            return content


# Backwards compatibility alias
TemplateManager = TemplatesManager
