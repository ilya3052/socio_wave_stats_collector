from typing import Optional

from telethon import TelegramClient
from vk_api.vk_api import VkApiMethod

from src.core import Platforms, KEY
from src.models import ServiceAccountDataModel
from src.tools import decrypt
from .apiTG import get_tg_api_session
from .apiVK import get_vk_api_session


async def get_api(account_data: ServiceAccountDataModel, platform):
    api: Optional[VkApiMethod | TelegramClient] = None
    if platform == Platforms.TG:
        api = get_tg_api_session(account_data.session_path)
    elif platform == Platforms.VK:
        api = get_vk_api_session(decrypt(account_data.service_key, KEY))
    return api
