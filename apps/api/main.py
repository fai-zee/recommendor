"""FastAPI application."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy import select

from services.workers import worker
from shared.db import session_scope
from shared.models import Account, Lead, Job

app = FastAPI()

API_KEY = os.getenv("API_KEY", "dev-local")


@app.middleware("http")
async def api_key_auth(request, call_next):
    if request.url.path == "/healthz" or request.url.path.startswith("/metrics"):
        return await call_next(request)
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/discover/hashtags")
def discover_hashtags(body: dict):
    queries = body.get("queries", [])
    worker.enqueue_discover_hashtags(queries)
    return {"enqueued": len(queries)}


@app.post("/discover/websearch")
async def discover_websearch(file: UploadFile = File(...)):
    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    worker.enqueue_import_csv(path)
    return {"status": "enqueued"}


@app.post("/discover/places")
def discover_places(body: dict):
    worker.enqueue_discover_maps(body.get("category", ""), body.get("city", ""))
    return {"status": "enqueued"}


@app.post("/enrich")
def enrich(body: dict):
    usernames = body.get("usernames", [])
    for u in usernames:
        worker.enqueue_enrich(u)
    return {"enqueued": len(usernames)}


@app.get("/leads")
def get_leads(
    min_confidence: float = 0.0,
    source: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    with session_scope() as session:
        stmt = select(Lead).join(Account).where(Lead.confidence >= min_confidence)
        if source:
            stmt = stmt.where(Account.source == source)
        leads = session.scalars(
            stmt.offset((page - 1) * page_size).limit(page_size)
        ).all()
        return [
            {
                "id": str(lead.id),
                "username": lead.account.username if lead.account else None,
                "confidence": float(lead.confidence or 0),
                "reason": lead.reason,
                "tags": lead.tags,
                "stage": lead.stage,
            }
            for lead in leads
        ]


@app.patch("/leads/{lead_id}")
def update_lead(lead_id: str, body: dict):
    with session_scope() as session:
        lead = session.get(Lead, lead_id)
        if not lead:
            raise HTTPException(404, "Lead not found")
        lead.stage = body.get("stage", lead.stage)
        lead.notes = body.get("notes", lead.notes)
        return {"id": lead_id}


@app.get("/jobs")
def get_jobs():
    with session_scope() as session:
        jobs = session.scalars(
            select(Job).order_by(Job.created_at.desc()).limit(100)
        ).all()
        return [
            {
                "id": str(j.id),
                "type": j.type,
                "status": j.status,
                "error": j.error,
            }
            for j in jobs
        ]


@app.get("/metrics")
def metrics():
    from prometheus_client import generate_latest

    return PlainTextResponse(generate_latest(), media_type="text/plain")
