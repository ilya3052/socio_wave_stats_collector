from typing import Optional

from telethon import TelegramClient
from vk_api.vk_api import VkApiMethod

from src.core import Platforms
from src.models import ServiceAccountDataModel
from .apiTG import get_tg_api_session
from .apiVK import get_vk_api_session


async def get_api(account_data: ServiceAccountDataModel, platform):
    api: Optional[VkApiMethod | TelegramClient] = None
    if platform == Platforms.TG:
        api = get_tg_api_session(account_data.session_path)
    elif platform == Platforms.VK:
        api = get_vk_api_session(account_data.service_key)
    return api
