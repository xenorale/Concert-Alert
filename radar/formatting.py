import html
import re

from . import config

_MONTHS = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]
_DATETIME = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})")


def human_date(value: str) -> str:
    match = _DATETIME.search(value or "")
    if not match:
        return ""
    year, month, day, hour, minute = (int(part) for part in match.groups())
    label = f"{day} {_MONTHS[month - 1]} {year}"
    if hour or minute:
        label += f", {hour:02d}:{minute:02d}"
    return label


def event_caption(artist_name: str, event: dict) -> str:
    lines = [f"🎵 <b>{html.escape(artist_name)}</b> выступит в городе {config.CITY_NAME}!", ""]
    title = (event.get("title") or "").strip()
    if title and title.lower() != artist_name.strip().lower():
        lines.append(f"🎤 {html.escape(title)}")
    date = human_date(event.get("start", ""))
    if date:
        lines.append(f"📅 {date}")
    venue = (event.get("venue") or "").strip()
    if venue:
        place = venue
        if event.get("address"):
            place += f", {event['address']}"
        lines.append(f"📍 {html.escape(place)}")
    lines.append("")
    lines.append(
        f'🎟 <a href="{html.escape(event.get("url", ""))}">Билеты и подробности на Афише</a>'
    )
    return "\n".join(lines)
