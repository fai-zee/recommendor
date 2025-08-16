"""RQ worker entrypoint."""

from __future__ import annotations

import os

import rq
from rq import Connection, Queue

from services.enrichment.enrichment_service import enrich_account
from services.ingestion.hashtag_service import discover_usernames
from services.ingestion.maps_pipeline import discover_from_maps
from services.ingestion.search_pivot import import_csv
from services.ranking.pipeline import score_account

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
connection = rq.Connection.from_url(redis_url)


def enqueue_discover_hashtags(queries: list[str]) -> rq.job.Job:
    with Connection(connection):
        q = Queue("discover")
        return q.enqueue(discover_usernames, queries)


def enqueue_import_csv(path: str) -> rq.job.Job:
    with Connection(connection):
        q = Queue("discover")
        return q.enqueue(import_csv, path)


def enqueue_discover_maps(category: str, city: str) -> rq.job.Job:
    with Connection(connection):
        q = Queue("discover")
        return q.enqueue(discover_from_maps, category, city)


def enqueue_enrich(username: str) -> rq.job.Job:
    with Connection(connection):
        q = Queue("enrich")
        return q.enqueue(enrich_account, username)


def enqueue_score(account_id: str) -> rq.job.Job:
    with Connection(connection):
        q = Queue("rank")
        return q.enqueue(score_account, account_id)


def run_worker() -> None:
    with Connection(connection):
        queues = [Queue("discover"), Queue("enrich"), Queue("rank")]
        worker = rq.Worker(queues)
        worker.work()
