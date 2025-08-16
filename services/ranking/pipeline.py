"""Ranking pipeline."""

from __future__ import annotations

from sqlalchemy import select

from shared.db import session_scope
from shared.models import Account, Lead

from .features import build_features
from .scorers import RuleScorer


scorer = RuleScorer()


def score_account(account_id: str) -> str:
    with session_scope() as session:
        account = session.get(Account, account_id)
        if not account:
            raise ValueError("account not found")
        features = build_features(account)
        score, reason = scorer.score(features)
        lead = session.scalar(select(Lead).where(Lead.account_id == account.id))
        if not lead:
            lead = Lead(account_id=account.id)
            session.add(lead)
        lead.confidence = score
        lead.reason = reason
        lead.tags = ["rule"]
        lead.stage = lead.stage or "NEW"
        return str(lead.id)
