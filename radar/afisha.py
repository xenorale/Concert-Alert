import json
import re

import requests

from . import config

_LD_BLOCK = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S
)
_EVENT_ID = re.compile(r"-(\d+)/?$")


def _page_url(page: int) -> str:
    base = config.AFISHA_BASE + config.AFISHA_SCHEDULE_PATH
    return base if page <= 1 else f"{base}page{page}/"


def _html(response: requests.Response) -> str:
    encoding = response.encoding
    if not encoding or encoding.lower() in ("iso-8859-1", "latin-1"):
        encoding = response.apparent_encoding or "utf-8"
    return response.content.decode(encoding, "replace")


def _absolute_url(url: str) -> str:
    url = (url or "").split("#")[0]
    if url.startswith("/"):
        url = config.AFISHA_BASE + url
    return url


def _first(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def _extract(html: str) -> list[dict]:
    events = []
    for block in _LD_BLOCK.findall(html):
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        for entry in payload.get("itemListElement", []):
            item = entry.get("item", {})
            if item.get("@type") == "MusicEvent":
                events.append(item)
    return events


def _address(location: dict) -> str:
    address = location.get("address")
    if isinstance(address, dict):
        return (address.get("streetAddress") or "").strip()
    if isinstance(address, str):
        return address.strip()
    return ""


def _to_event(item: dict) -> dict | None:
    url = _absolute_url(item.get("url", ""))
    if not url:
        return None
    location = item.get("location")
    if not isinstance(location, dict):
        location = {}
    match = _EVENT_ID.search(url)
    return {
        "id": match.group(1) if match else url,
        "title": (item.get("name") or "").strip(),
        "url": url,
        "image": _first(item.get("image")),
        "start": item.get("startDate") or "",
        "venue": (location.get("name") or "").strip(),
        "address": _address(location),
    }


def fetch_events() -> list[dict]:
    session = requests.Session()
    session.headers.update(
        {"User-Agent": config.USER_AGENT, "Accept-Language": "ru,en;q=0.9"}
    )
    seen: set[str] = set()
    events: list[dict] = []
    for page in range(1, config.AFISHA_MAX_PAGES + 1):
        try:
            response = session.get(_page_url(page), timeout=config.REQUEST_TIMEOUT)
        except requests.RequestException:
            break
        if response.status_code != 200:
            break
        raw = _extract(_html(response))
        fresh = 0
        for item in raw:
            event = _to_event(item)
            if event is None or event["url"] in seen:
                continue
            seen.add(event["url"])
            events.append(event)
            fresh += 1
        if not raw or fresh == 0:
            break
    return events
