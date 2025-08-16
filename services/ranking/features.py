"""Feature builders for ranking."""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from shared.models import Account

KEYWORDS = ["bakery", "boulangerie", "patisserie", "bakkerij"]
CITY_KEYWORDS = ["amsterdam", "jordaan", "de pijp", "oud-west"]


def build_features(account: Account) -> Dict[str, float]:
    feats: Dict[str, float] = {}
    bio = (account.bio or "").lower()
    feats["bio_keyword"] = 1.0 if any(k in bio for k in KEYWORDS) else 0.0
    feats["category_keyword"] = (
        1.0 if (account.category or "").lower() in KEYWORDS else 0.0
    )
    feats["website_nl"] = (
        1.0 if account.website and account.website.endswith(".nl") else 0.0
    )
    followers = (account.metrics_json or {}).get("followers_count", 0) or 0
    feats["followers_bucket"] = min(followers / 1000.0, 10.0)
    feats["media_count"] = float(
        (account.metrics_json or {}).get("media_count", 0) or 0
    )
    if account.last_post_at:
        delta = datetime.utcnow() - account.last_post_at
        feats["days_since_post"] = delta.days
    else:
        feats["days_since_post"] = 999.0
    src = (account.source or "").lower()
    feats["source_hashtag"] = 1.0 if src == "hashtag" else 0.0
    feats["source_maps"] = 1.0 if src == "maps" else 0.0
    feats["city_keyword"] = 1.0 if any(k in bio for k in CITY_KEYWORDS) else 0.0
    return feats
