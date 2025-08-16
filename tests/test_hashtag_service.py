from __future__ import annotations

from services.ingestion import hashtag_service
from shared.db import Base, engine


def setup_module(module):
    Base.metadata.create_all(engine)


def teardown_module(module):
    Base.metadata.drop_all(engine)


def test_discover_usernames(monkeypatch):
    def fake_search(q):
        return [{"id": "1"}]

    def fake_media(hashtag_id, cursor):
        return iter([{"username": "user1"}, {"username": "user2"}])

    monkeypatch.setattr(
        hashtag_service.graph_client, "ig_hashtag_search", lambda q: fake_search(q)
    )
    monkeypatch.setattr(
        hashtag_service, "fetch_recent_media", lambda hid, c: fake_media(hid, c)
    )
    handles = hashtag_service.discover_usernames(["bread"])
    assert set(handles) == {"user1", "user2"}
