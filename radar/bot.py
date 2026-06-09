import html

from . import checker, config, music, storage
from .telegram import Telegram

HELP = (
    "🎸 <b>Концертный радар · {city}</b>\n\n"
    "Я слежу за концертами твоих артистов и пишу, когда кто-то из них едет к нам.\n\n"
    "<b>Команды</b>\n"
    "• просто пришли имя артиста — добавлю его\n"
    "• /add <i>артист</i> — добавить артиста\n"
    "• /remove <i>артист</i> — убрать артиста\n"
    "• /list — мои артисты\n"
    "• /search <i>артист</i> — найти артиста, не добавляя\n"
    "• /check — проверить афишу прямо сейчас\n"
    "• /help — эта справка"
).format(city=config.CITY_NAME)


def _clean(text: str) -> str:
    return " ".join(text.split())


def _find(artists: list[dict], query: str) -> dict | None:
    query = query.lower()
    for artist in artists:
        if artist.get("query", "").lower() == query or (artist.get("name") or "").lower() == query:
            return artist
    return None


def _artist_label(info: dict | None) -> str:
    if not info:
        return ""
    fans = info.get("fans") or 0
    return f"\n👥 {fans:,} слушателей на Deezer".replace(",", " ") if fans else ""


def handle_start(telegram: Telegram, chat: int) -> None:
    telegram.send_message(chat, HELP)


def handle_add(telegram: Telegram, chat: int, query: str, artists: list[dict]) -> None:
    query = _clean(query)
    if not query:
        telegram.send_message(chat, "Напиши имя артиста, например: <code>/add Скриптонит</code>")
        return
    if _find(artists, query):
        telegram.send_message(chat, f"«{html.escape(query)}» уже в списке. /list")
        return

    info = music.resolve_artist(query)
    artist = {
        "query": query,
        "name": (info or {}).get("name", query),
        "picture": (info or {}).get("picture", ""),
        "deezer_id": (info or {}).get("deezer_id"),
        "link": (info or {}).get("link", ""),
        "fans": (info or {}).get("fans", 0),
    }
    artists.append(artist)
    storage.save_artists(artists)

    caption = (
        f"✅ Добавил: <b>{html.escape(artist['name'])}</b>{_artist_label(info)}\n\n"
        f"Сообщу, как только появится концерт в городе {config.CITY_NAME}."
    )
    if artist["picture"]:
        telegram.send_photo(chat, artist["picture"], caption)
    else:
        telegram.send_message(chat, caption)

    delivered = checker.run(only_artist=artist, chats=[chat])
    if delivered == 0:
        telegram.send_message(
            chat, f"Пока концертов в городе {config.CITY_NAME} нет — буду держать руку на пульсе."
        )


def handle_remove(telegram: Telegram, chat: int, query: str, artists: list[dict]) -> None:
    query = _clean(query)
    artist = _find(artists, query)
    if not artist:
        telegram.send_message(chat, f"Не нашёл «{html.escape(query)}» в списке. /list")
        return
    artists.remove(artist)
    storage.save_artists(artists)
    telegram.send_message(chat, f"🗑 Убрал: <b>{html.escape(artist.get('name') or query)}</b>")


def handle_list(telegram: Telegram, chat: int, artists: list[dict]) -> None:
    if not artists:
        telegram.send_message(chat, "Список пуст. Пришли имя артиста, чтобы добавить.")
        return
    rows = "\n".join(
        f"{index}. {html.escape(artist.get('name') or artist.get('query'))}"
        for index, artist in enumerate(artists, start=1)
    )
    telegram.send_message(chat, f"🎧 <b>Твои артисты ({len(artists)})</b>\n\n{rows}")


def handle_search(telegram: Telegram, chat: int, query: str) -> None:
    query = _clean(query)
    if not query:
        telegram.send_message(chat, "Кого ищем? <code>/search Three Days Grace</code>")
        return
    info = music.resolve_artist(query)
    if not info:
        telegram.send_message(chat, f"Ничего не нашёл по запросу «{html.escape(query)}».")
        return
    caption = (
        f"<b>{html.escape(info['name'])}</b>{_artist_label(info)}\n\n"
        f"Добавить: <code>/add {html.escape(info['name'])}</code>"
    )
    if info.get("picture"):
        telegram.send_photo(chat, info["picture"], caption)
    else:
        telegram.send_message(chat, caption)


def handle_check(telegram: Telegram, chat: int) -> None:
    telegram.send_message(chat, "🔎 Проверяю афишу…")
    delivered = checker.run(chats=[chat], respect_notified=False, record=False)
    if delivered == 0:
        telegram.send_message(
            chat, f"Сейчас концертов твоих артистов в городе {config.CITY_NAME} нет."
        )


def _dispatch(telegram: Telegram, chat: int, text: str, artists: list[dict]) -> None:
    if not text:
        telegram.send_message(chat, "Пришли имя артиста или используй /help.")
        return
    if text.startswith("/"):
        head, _, tail = text.partition(" ")
        command = head.split("@")[0].lower()
        argument = tail.strip()
        if command == "/start":
            handle_start(telegram, chat)
        elif command == "/help":
            telegram.send_message(chat, HELP)
        elif command == "/add":
            handle_add(telegram, chat, argument, artists)
        elif command in ("/remove", "/del", "/delete"):
            handle_remove(telegram, chat, argument, artists)
        elif command in ("/list", "/artists"):
            handle_list(telegram, chat, artists)
        elif command in ("/search", "/find"):
            handle_search(telegram, chat, argument)
        elif command == "/check":
            handle_check(telegram, chat)
        else:
            telegram.send_message(chat, "Не знаю такую команду. /help")
    else:
        handle_add(telegram, chat, text, artists)


def run_bot() -> None:
    telegram = Telegram()
    state = storage.load_bot_state()
    offset = state.get("offset", 0)
    updates = telegram.get_updates(offset + 1 if offset else 0)
    if not updates:
        return

    artists = storage.load_artists()
    subscribers = storage.load_subscribers()
    subscribers_changed = False

    for update in updates:
        offset = max(offset, update["update_id"])
        message = update.get("message") or {}
        chat = (message.get("chat") or {}).get("id")
        if chat is None:
            continue
        if chat not in subscribers:
            subscribers.append(chat)
            subscribers_changed = True
        _dispatch(telegram, chat, (message.get("text") or "").strip(), artists)

    state["offset"] = offset
    storage.save_bot_state(state)
    if subscribers_changed:
        storage.save_subscribers(subscribers)
