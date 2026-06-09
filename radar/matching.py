import re

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = (text or "").lower().replace("ё", "е")
    text = _PUNCT.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def match_terms(artist: dict) -> list[str]:
    terms = {normalize(artist.get("query", "")), normalize(artist.get("name", ""))}
    for alias in artist.get("aliases", []):
        terms.add(normalize(alias))
    return [term for term in terms if len(term) >= 2]


def title_matches(title: str, terms: list[str]) -> bool:
    normalized = normalize(title)
    for term in terms:
        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized):
            return True
    return False
