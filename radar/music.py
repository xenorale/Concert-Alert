import requests

from . import config


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": config.USER_AGENT})
    return session


def resolve_artist(query: str) -> dict | None:
    query = " ".join(query.split())
    if not query:
        return None
    try:
        response = _session().get(
            f"{config.DEEZER_API}/search/artist",
            params={"q": query, "limit": 5},
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("data", [])
    except (requests.RequestException, ValueError):
        return None
    if not results:
        return None
    best = results[0]
    picture = (
        best.get("picture_xl")
        or best.get("picture_big")
        or best.get("picture_medium")
        or ""
    )
    return {
        "name": best.get("name", query),
        "picture": picture,
        "deezer_id": best.get("id"),
        "link": best.get("link", ""),
        "fans": best.get("nb_fan", 0),
    }
