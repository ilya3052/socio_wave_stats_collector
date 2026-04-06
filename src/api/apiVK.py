from typing import Optional

from vk_api.vk_api import VkApiMethod, VkApi


def get_vk_api_session(service_key):
    try:
        vk_api: Optional[VkApiMethod] = VkApi(token=service_key).get_api()
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

    if vk_api:
        return vk_api
    return None
