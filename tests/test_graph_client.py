from __future__ import annotations

import json
from pathlib import Path

import requests  # type: ignore[import]

from shared import graph_client


class DummyResponse:
    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


def test_retry_rate_limit(monkeypatch):
    fixtures = [
        (429, json.load(open(Path("tests/data/rate_limit.json")))),
        (200, json.load(open(Path("tests/data/business_success.json")))),
    ]
    calls = {"n": 0}

    def fake_request(method, url, params=None, timeout=10):
        code, data = fixtures[calls["n"]]
        calls["n"] += 1
        return DummyResponse(code, data)

    monkeypatch.setattr(requests, "request", fake_request)
    data = graph_client._request("GET", "test", {})
    assert data["business_discovery"]["username"] == "testbakery"
