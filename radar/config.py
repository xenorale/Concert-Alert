import os

CITY_NAME = "Воронеж"

AFISHA_BASE = "https://www.afisha.ru"
AFISHA_SCHEDULE_PATH = "/voronezh/schedule_concert/"
AFISHA_MAX_PAGES = 15

DEEZER_API = "https://api.deezer.com"
TELEGRAM_API = "https://api.telegram.org"

REQUEST_TIMEOUT = 25
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_ROOT, "data")
ARTISTS_FILE = os.path.join(DATA_DIR, "artists.json")
SUBSCRIBERS_FILE = os.path.join(DATA_DIR, "subscribers.json")
BOT_STATE_FILE = os.path.join(DATA_DIR, "bot_state.json")
SENT_FILE = os.path.join(DATA_DIR, "sent.json")


def bot_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return token
