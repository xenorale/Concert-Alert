import json
import os
from typing import Any

from . import config


def _read(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write(path: str, value: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_artists() -> list[dict]:
    return _read(config.ARTISTS_FILE, [])


def save_artists(artists: list[dict]) -> None:
    _write(config.ARTISTS_FILE, artists)


def load_subscribers() -> list[int]:
    return _read(config.SUBSCRIBERS_FILE, [])


def save_subscribers(subscribers: list[int]) -> None:
    _write(config.SUBSCRIBERS_FILE, sorted(set(subscribers)))


def load_bot_state() -> dict:
    return _read(config.BOT_STATE_FILE, {"offset": 0})


def save_bot_state(state: dict) -> None:
    _write(config.BOT_STATE_FILE, state)


def load_sent() -> dict:
    return _read(config.SENT_FILE, {"notified": [], "last_check": None})


def save_sent(sent: dict) -> None:
    _write(config.SENT_FILE, sent)
