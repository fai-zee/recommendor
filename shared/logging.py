"""Logging configuration."""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )
