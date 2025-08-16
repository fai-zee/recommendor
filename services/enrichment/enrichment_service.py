"""Account enrichment service."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select

from shared import graph_client
from shared.db import session_scope
from shared.models import Account, Audit

BUSINESS_FIELDS = [
    "username",
    "name",
    "biography",
    "website",
    "profile_picture_url",
    "media_count",
    "followers_count",
    "follows_count",
    "category",
    "category_name",
]


def enrich_account(username: str, force: bool = False) -> None:
    with session_scope() as session:
        account = session.scalar(select(Account).where(Account.username == username))
        if not account:
            account = Account(username=username, source="manual", status="DISCOVERED")
            session.add(account)
            session.flush()
        if account.updated_at and not force:
            if datetime.utcnow() - account.updated_at < timedelta(days=7):
                return
        data = graph_client.business_discovery(username, BUSINESS_FIELDS)
        if not data:
            account.status = "NOT_FOUND"
            return
        if not data.get("is_business_account") and not data.get(
            "is_professional_account"
        ):
            account.status = "NOT_PRO_ACCOUNT"
            return
        account.name = data.get("name")
        account.bio = data.get("biography")
        account.website = data.get("website")
        account.profile_pic_url = data.get("profile_picture_url")
        account.metrics_json = {
            "media_count": data.get("media_count"),
            "followers_count": data.get("followers_count"),
            "follows_count": data.get("follows_count"),
        }
        account.category = data.get("category_name") or data.get("category")
        account.is_professional = True
        account.status = "ENRICHED"
        session.add(
            Audit(
                action="enrich",
                entity="account",
                entity_id=str(account.id),
                payload_json=data,
            )
        )
