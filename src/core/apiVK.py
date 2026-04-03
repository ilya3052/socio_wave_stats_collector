from typing import Optional

from vk_api.vk_api import VkApiMethod, VkApi

from .config import SERVICE_KEY


def get_vk_api_session():
    try:
        vk_api: Optional[VkApiMethod] = VkApi(token=SERVICE_KEY).get_api()
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

    if vk_api:
        return vk_api
    return None
