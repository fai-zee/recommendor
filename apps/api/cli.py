"""CLI helper."""

from __future__ import annotations

import typer

from services.workers import worker

app = typer.Typer()


@app.command()
def discover_hashtags(queries: list[str]):
    worker.enqueue_discover_hashtags(queries)


@app.command()
def import_web_csv(file: str):
    worker.enqueue_import_csv(file)


@app.command()
def discover_places(category: str, city: str):
    worker.enqueue_discover_maps(category, city)


@app.command()
def score_leads(rebuild_model: bool = False):
    # Placeholder: in MVP we just print
    print("scoring leads", rebuild_model)


if __name__ == "__main__":
    app()
