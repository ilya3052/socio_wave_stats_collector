import logging
from typing import Optional

from vk_api.vk_api import VkApiMethod, VkApi

logger = logging.getLogger(__name__)


def get_vk_api_session(service_key):
    try:
        vk_api: Optional[VkApiMethod] = VkApi(token=service_key).get_api()
        logger.debug("Объект VK API создан")
        return vk_api
    except Exception as e:
        logger.exception(f"Ошибка создания объекта VK API: {e}")
        return None
