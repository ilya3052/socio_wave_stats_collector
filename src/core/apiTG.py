from typing import Optional

from telethon import TelegramClient

from .config import API_HASH, API_ID, SESSION_PATH


def get_tg_api_session():
    try:
        tg_api: Optional[TelegramClient] = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    except Exception as e:
        print('Ошибка при получении api')
        return None

    if tg_api:
        return tg_api
    return None
