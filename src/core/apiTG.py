from typing import Optional

from telethon import TelegramClient

from .config import API_HASH, API_ID, SESSION_PATH


def get_tg_api_session():
    try:
        tg_api: Optional[TelegramClient] = TelegramClient(api_id=API_ID, api_hash=API_HASH, session=SESSION_PATH)
    except Exception as e:
        print('Ошибка при получении api', e)
        return None

    if tg_api:
        return tg_api
    return None
