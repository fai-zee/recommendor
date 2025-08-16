from __future__ import annotations

from datetime import datetime, timedelta

from services.ranking.features import build_features
from shared.models import Account


def test_build_features():
    acc = Account(
        username="u",
        bio="Great bakery in Amsterdam",
        website="https://test.nl",
        metrics_json={"followers_count": 1200, "media_count": 5},
        last_post_at=datetime.utcnow() - timedelta(days=10),
        source="hashtag",
    )
    feats = build_features(acc)
    assert feats["bio_keyword"] == 1.0
    assert feats["website_nl"] == 1.0
    assert feats["followers_bucket"] == 1.2
