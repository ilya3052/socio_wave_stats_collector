from typing import Optional

from telethon import TelegramClient

from src.core.config import API_HASH, API_ID


def get_tg_api_session(session_path):
    try:
        tg_api: Optional[TelegramClient] = TelegramClient(api_id=API_ID, api_hash=API_HASH, session=session_path)
    except Exception as e:
        print('Ошибка при получении api', e)
        return None

    if tg_api:
        return tg_api
    return None
