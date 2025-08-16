"""Web search CSV importer."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import List

from sqlalchemy import select

from shared.db import session_scope
from shared.models import Account

HANDLE_RE = re.compile(r"instagram\.com/([A-Za-z0-9_\.]+)")


def parse_urls_to_handles(urls: List[str]) -> List[str]:
    handles: set[str] = set()
    for url in urls:
        match = HANDLE_RE.search(url)
        if match:
            handles.add(match.group(1).lower())
    return list(handles)


def persist_handles(handles: List[str], source: str = "web_search") -> dict:
    inserted = 0
    duplicates = 0
    with session_scope() as session:
        for handle in handles:
            existing = session.scalar(select(Account).where(Account.username == handle))
            if existing:
                duplicates += 1
                continue
            acc = Account(username=handle, source=source, status="DISCOVERED")
            session.add(acc)
            inserted += 1
    return {"inserted": inserted, "duplicates": duplicates, "total": len(handles)}


def import_csv(file_path: Path) -> dict:
    urls: list[str] = []
    with file_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "url" in row:
                urls.append(row["url"])
    handles = parse_urls_to_handles(urls)
    result = persist_handles(handles)
    result["valid_handles"] = len(handles)
    return result
