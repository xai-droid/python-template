from pathlib import Path
import json
import time
import tempfile
import os
from threading import RLock
from typing import Any, Callable, Dict, Optional, List

DEFAULT_CACHE_FILE = Path.home() / ".python_new_cache.json"
_LOCK = RLock()

class SimpleCache:
    def __init__(self, path: Optional[Path] = None, max_entries: int = 500):
        self.path = Path(path) if path else DEFAULT_CACHE_FILE
        self.max_entries = max_entries
        self._data: Dict[str, Dict[str, Any]] = {}
        # structure: key -> {"value": ..., "expires": float|None, "updated": float}
        self._loaded = False

    def _atomic_write(self, data: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=self.path.name, dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)
            os.replace(tmp, str(self.path))
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass

    def _load(self) -> None:
        with _LOCK:
            if self._loaded:
                return
            if not self.path.exists():
                self._data = {}
                self._loaded = True
                return
            try:
                raw = self.path.read_text(encoding="utf-8")
                obj = json.loads(raw) if raw else {}
                # validate shape
                if isinstance(obj, dict):
                    self._data = obj
                else:
                    self._data = {}
            except Exception:
                # corrupted -> reset
                self._data = {}
            self._loaded = True
            self._prune_expired_locked()

    def _save(self) -> None:
        with _LOCK:
            self._prune_expired_locked()
            s = json.dumps(self._data, ensure_ascii=False, indent=2, default=str)
            self._atomic_write(s)

    def _prune_expired_locked(self) -> None:
        now = time.time()
        keys_to_delete = [k for k, v in self._data.items() if v.get("expires") and v["expires"] <= now]
        for k in keys_to_delete:
            self._data.pop(k, None)
        # enforce max_entries by updated timestamp (oldest removed)
        if self.max_entries and len(self._data) > self.max_entries:
            items = sorted(self._data.items(), key=lambda kv: kv[1].get("updated", 0))
            for k, _ in items[: len(self._data) - self.max_entries]:
                self._data.pop(k, None)

    def get(self, key: str, default: Any = None) -> Any:
        self._load()
        with _LOCK:
            item = self._data.get(key)
            if not item:
                return default
            expires = item.get("expires")
            if expires and expires <= time.time():
                # expired
                self._data.pop(key, None)
                self._save()
                return default
            return item.get("value", default)

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set key to value. ttl in seconds (optional).
        """
        self._load()
        with _LOCK:
            expires = time.time() + ttl if ttl else None
            self._data[key] = {"value": value, "expires": expires, "updated": time.time()}
            self._prune_expired_locked()
            self._save()

    def delete(self, key: str) -> bool:
        self._load()
        with _LOCK:
            if key in self._data:
                self._data.pop(key, None)
                self._save()
                return True
            return False

    def clear(self) -> None:
        with _LOCK:
            self._data = {}
            self._save()

    def keys(self) -> List[str]:
        self._load()
        with _LOCK:
            self._prune_expired_locked()
            return list(self._data.keys())

    def size(self) -> int:
        self._load()
        with _LOCK:
            self._prune_expired_locked()
            return len(self._data)

    def get_or_compute(self, key: str, fn: Callable[[], Any], ttl: Optional[float] = None) -> Any:
        """
        Return cached value or compute via fn(), store it with optional ttl, and return it.
        fn is only called when value is missing/expired.
        """
        val = self.get(key, None)
        if val is not None:
            return val
        # compute and store
        result = fn()
        self.set(key, result, ttl=ttl)
        return result

# module-level convenience instance
_default_cache = SimpleCache()

def load_cache() -> Dict[str, Any]:
    """Return raw cache dict (internal structure)."""
    _default_cache._load()
    return dict(_default_cache._data)

def save_cache(content: Dict[str, Any]) -> None:
    """Overwrite cache with provided raw dict (must follow internal structure)."""
    with _LOCK:
        _default_cache._data = content or {}
        _default_cache._save()

def get(key: str, default: Any = None) -> Any:
    return _default_cache.get(key, default)

def set(key: str, value: Any, ttl: Optional[float] = None) -> None:
    _default_cache.set(key, value, ttl=ttl)

def delete(key: str) -> bool:
    return _default_cache.delete(key)

def clear() -> None:
    _default_cache.clear()

def keys() -> List[str]:
    return _default_cache.keys()

def size() -> int:
    return _default_cache.size()

def get_or_compute(key: str, fn: Callable[[], Any], ttl: Optional[float] = None) -> Any:
    return _default_cache.get_or_compute(key, fn, ttl=ttl)
