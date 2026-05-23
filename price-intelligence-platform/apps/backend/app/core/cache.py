from __future__ import annotations

import json
import time
from typing import Any


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)

    def invalidate_prefix(self, prefix: str) -> None:
        for key in list(self._store):
            if key.startswith(prefix):
                self._store.pop(key, None)


cache = TTLCache()


def cache_key(*parts: Any) -> str:
    return ":".join(json.dumps(part, sort_keys=True, default=str) for part in parts)
