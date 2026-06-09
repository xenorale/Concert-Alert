import datetime as dt

from . import afisha, formatting, storage
from .matching import match_terms, title_matches
from .telegram import Telegram


def find_matches(artists: list[dict], events: list[dict]) -> list[tuple[dict, dict]]:
    pairs = []
    for artist in artists:
        terms = match_terms(artist)
        if not terms:
            continue
        for event in events:
            if title_matches(event["title"], terms):
                pairs.append((artist, event))
    return pairs


def run(
    only_artist: dict | None = None,
    chats: list[int] | None = None,
    respect_notified: bool = True,
    record: bool = True,
) -> int:
    artists = [only_artist] if only_artist else storage.load_artists()
    if not artists:
        return 0
    chats = chats if chats is not None else storage.load_subscribers()
    if not chats:
        return 0

    events = afisha.fetch_events()
    if not events:
        return 0

    sent = storage.load_sent()
    notified = set(sent.get("notified", []))
    telegram = Telegram()
    delivered: set[str] = set()

    for artist, event in find_matches(artists, events):
        name = artist.get("name") or artist.get("query")
        caption = formatting.event_caption(name, event)
        photo = event.get("image") or artist.get("picture")
        for chat in chats:
            key = f"{chat}:{event['id']}"
            if key in delivered:
                continue
            if respect_notified and key in notified:
                continue
            if photo:
                telegram.send_photo(chat, photo, caption)
            else:
                telegram.send_message(chat, caption)
            delivered.add(key)

    if record:
        sent["notified"] = sorted(notified | delivered)
        sent["last_check"] = dt.datetime.now(dt.timezone.utc).isoformat()
        storage.save_sent(sent)
    return len(delivered)
