# Instagram Lead Generation MVP

This repository contains a minimal implementation of an Instagram lead-generation pipeline.  
It includes FastAPI API, ingestion services, enrichment via the Instagram Graph API, ranking, and worker queues.

## Layout

```
apps/api           - FastAPI application and CLI helpers
services/ingestion - discovery pipelines (hashtags, web CSV, maps)
services/enrichment- account enrichment
services/ranking   - feature building and scoring
services/workers   - RQ worker and enqueue helpers
shared             - shared utilities and models
infra/docker       - docker-compose setup for local dev
```

## Development

```
python -m black .
python -m ruff check .
python -m mypy --ignore-missing-imports .
python -m pytest
```
