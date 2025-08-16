"""Hashtag discovery service."""

from __future__ import annotations

from typing import Iterator, List

from sqlalchemy import select

from shared import graph_client
from shared.db import session_scope
from shared.models import Account


def search_ids(queries: List[str]) -> List[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for q in queries:
        results = graph_client.ig_hashtag_search(q)
        for item in results:
            hid = item.get("id")
            if hid and hid not in seen:
                seen.add(hid)
                ids.append(hid)
    return ids


def fetch_recent_media(
    hashtag_id: str, since_cursor: str | None = None
) -> Iterator[dict]:
    cursor = since_cursor
    while True:
        data = graph_client.hashtag_recent_media(hashtag_id, cursor)
        for item in data.get("data", []):
            yield item
        cursor = data.get("paging", {}).get("cursors", {}).get("after")
        if not cursor:
            break


def discover_usernames(queries: List[str]) -> List[str]:
    usernames: set[str] = set()
    hashtag_ids = search_ids(queries)
    for hid in hashtag_ids:
        for media in fetch_recent_media(hid, None):
            username = media.get("username")
            if username:
                usernames.add(username.lower())
                _persist_account(username, "hashtag", {"hashtag_id": hid})
    return list(usernames)


def _persist_account(username: str, source: str, details: dict) -> None:
    with session_scope() as session:
        existing = session.scalar(select(Account).where(Account.username == username))
        if existing:
            return
        acc = Account(
            username=username,
            source=source,
            source_details=details,
            status="DISCOVERED",
        )
        session.add(acc)
