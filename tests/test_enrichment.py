import json
from pathlib import Path
import sqlalchemy as sa

from services.enrichment import enrichment_service
from shared.db import Base, engine, session_scope
from shared.models import Account


def setup_module(module):
    Base.metadata.create_all(engine)


def teardown_module(module):
    Base.metadata.drop_all(engine)


def test_enrich_account(monkeypatch):
    data = json.load(open(Path("tests/data/business_success.json")))[
        "business_discovery"
    ]
    monkeypatch.setattr(
        enrichment_service.graph_client, "business_discovery", lambda u, f: data
    )
    enrichment_service.enrich_account("testbakery")
    with session_scope() as session:
        acc = session.scalar(sa.select(Account).where(Account.username == "testbakery"))
        assert acc.name == "Test Bakery"
        assert acc.status == "ENRICHED"
