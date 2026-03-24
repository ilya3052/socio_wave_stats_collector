from typing import Optional

from vk_api.vk_api import VkApiMethod, VkApi

from core.config import SERVICE_KEY


def get_vk_api_session():
    vk: Optional[VkApiMethod] = None
    try:
        vk = VkApi(token=SERVICE_KEY).get_api()
    except Exception as e:
        print(f"Ошибка: {e}")

    if vk:
        return vk
    return None

vk: VkApiMethod = get_vk_api_session()