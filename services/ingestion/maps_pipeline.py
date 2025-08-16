"""Maps + website inspector pipeline (stub)."""

from __future__ import annotations

import re
import time
from typing import List

import requests  # type: ignore[import]
from sqlalchemy import select

from shared.db import session_scope
from shared.models import Account

HANDLE_RE = re.compile(r"instagram\.com/([A-Za-z0-9_\.]+)")


class PlacesProvider:
    def search(self, category: str, city: str) -> List[str]:
        # Stub provider returns fixture websites
        return [
            "https://example.com/bakery1",
            "https://example.com/bakery2",
            "https://example.com/bakery3",
        ]


def find_instagram_links(url: str) -> List[str]:
    time.sleep(1)  # throttle
    try:
        resp = requests.get(url, timeout=5)
    except Exception:
        return []
    return [m.group(1).lower() for m in HANDLE_RE.finditer(resp.text)]


def discover_from_maps(category: str, city: str) -> List[str]:
    provider = PlacesProvider()
    websites = provider.search(category, city)
    handles: set[str] = set()
    for url in websites:
        handles.update(find_instagram_links(url))
    persist_handles(list(handles), source="maps")
    return list(handles)


def persist_handles(handles: List[str], source: str) -> None:
    with session_scope() as session:
        for handle in handles:
            existing = session.scalar(select(Account).where(Account.username == handle))
            if existing:
                continue
            acc = Account(username=handle, source=source, status="DISCOVERED")
            session.add(acc)
