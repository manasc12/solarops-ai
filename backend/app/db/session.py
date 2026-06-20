"""In-memory data store.

A lightweight, thread-safe singleton store standing in for PostgreSQL. It keeps
the system fully runnable with zero external infrastructure while preserving the
repository abstraction so a real database can be swapped in later.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any


class InMemoryStore:
    """Process-wide key/collection store guarded by a lock."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._collections: dict[str, dict[str, Any]] = defaultdict(dict)

    def put(self, collection: str, key: str, value: Any) -> None:
        with self._lock:
            self._collections[collection][key] = value

    def get(self, collection: str, key: str) -> Any | None:
        with self._lock:
            return self._collections[collection].get(key)

    def list(self, collection: str) -> list[Any]:
        with self._lock:
            return list(self._collections[collection].values())

    def delete(self, collection: str, key: str) -> None:
        with self._lock:
            self._collections[collection].pop(key, None)

    def clear(self, collection: str | None = None) -> None:
        with self._lock:
            if collection is None:
                self._collections.clear()
            else:
                self._collections[collection].clear()


_store: InMemoryStore | None = None
_store_lock = threading.Lock()


def get_store() -> InMemoryStore:
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                _store = InMemoryStore()
    return _store
