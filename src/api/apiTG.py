import logging

from telethon import TelegramClient

from src.core import API_HASH, API_ID

logger = logging.getLogger(__name__)


def get_tg_api_session(session_path):
    try:
        tg_api = TelegramClient(api_id=API_ID, api_hash=API_HASH, session=session_path)
        logger.debug(f"TelegramClient создан для сессии {session_path}")
        return tg_api
    except Exception as e:
        logger.exception(f"Ошибка создания TelegramClient: {e}")
        return None
