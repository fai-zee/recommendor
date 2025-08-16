"""Minimal Instagram Graph API client."""

from __future__ import annotations

import os
import random
import time
from typing import Any, Dict

import requests  # type: ignore[import]

BASE_URL = "https://graph.facebook.com/v20.0"

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_USER_TOKEN = os.getenv("FB_USER_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")


class GraphAPIError(Exception):
    def __init__(self, code: int, message: str, subcode: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.subcode = subcode


def _request(method: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}/{path}"
    backoff = 1.0
    for attempt in range(5):
        resp = requests.request(method, url, params=params, timeout=10)
        if resp.status_code in (429, 500, 502, 503, 504):
            wait = backoff + random.random()
            time.sleep(wait)
            backoff = min(backoff * 2, 60)
            continue
        if resp.status_code != 200:
            data = resp.json().get("error", {})
            raise GraphAPIError(
                data.get("code", 0), data.get("message", ""), data.get("error_subcode")
            )
        return resp.json()
    raise GraphAPIError(429, "Too many retries")


def ig_hashtag_search(q: str) -> list[dict]:
    params = {"q": q, "access_token": FB_USER_TOKEN}
    data = _request("GET", "ig_hashtag_search", params)
    return data.get("data", [])


def hashtag_recent_media(hashtag_id: str, after: str | None = None) -> dict:
    params = {
        "user_id": IG_USER_ID,
        "fields": "id,caption,permalink,media_type,timestamp,username",
        "access_token": FB_USER_TOKEN,
    }
    if after:
        params["after"] = after
    return _request("GET", f"{hashtag_id}/recent_media", params)


def business_discovery(username: str, fields: list[str]) -> dict | None:
    params = {
        "access_token": FB_USER_TOKEN,
        "fields": f"business_discovery.username({username}){{{','.join(fields)}}}",
    }
    try:
        data = _request("GET", IG_USER_ID or "", params)
    except GraphAPIError as exc:
        if exc.code == 190:  # invalid token etc.
            return None
        raise
    return data.get("business_discovery")
