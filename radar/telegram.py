import requests

from . import config


class Telegram:
    def __init__(self, token: str | None = None):
        self.token = token or config.bot_token()
        self.base = f"{config.TELEGRAM_API}/bot{self.token}"
        self.session = requests.Session()

    def _call(self, method: str, payload: dict) -> dict:
        try:
            response = self.session.post(
                f"{self.base}/{method}", json=payload, timeout=config.REQUEST_TIMEOUT
            )
            return response.json()
        except (requests.RequestException, ValueError):
            return {"ok": False}

    def send_message(self, chat_id: int, text: str, **extra) -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        payload.update(extra)
        return self._call("sendMessage", payload)

    def send_photo(self, chat_id: int, photo: str, caption: str, **extra) -> dict:
        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "parse_mode": "HTML",
        }
        payload.update(extra)
        result = self._call("sendPhoto", payload)
        if not result.get("ok"):
            return self.send_message(chat_id, caption)
        return result

    def get_updates(self, offset: int, timeout: int = 0) -> list[dict]:
        result = self._call(
            "getUpdates",
            {"offset": offset, "timeout": timeout, "allowed_updates": ["message"]},
        )
        return result.get("result", []) if result.get("ok") else []
