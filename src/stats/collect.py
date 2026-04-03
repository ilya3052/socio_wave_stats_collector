from typing import Optional, List, Dict

from telethon import TelegramClient
from vk_api.vk_api import VkApiMethod

from src.core import Session, Platforms, get_vk_api_session
from src.core.apiTG import get_tg_api_session
from src.handlers import handle_vk_group, handle_tg_group
from src.models import GroupSchema
from src.repositories import GroupsRepository


async def get_groups(platform_id):
    groups: Optional[List[GroupSchema]] = None

    with Session() as session:
        repo = GroupsRepository(session)
        groups: List[GroupSchema] = [GroupSchema.model_validate(group) for group in
                                     repo.get_groups_by_platform(platform_id)]

    return groups


async def collect_vk_stats(api, groups, **kwargs):
    stats: List[Dict[str, str | int]] = []
    for group in groups:  # type: GroupSchema
        stats.append(await handle_vk_group(**{
            "group": group,
            "api": api,
            "options": kwargs
        }))
    return stats


async def collect_tg_stats(api, groups, **kwargs):
    stats: List[Dict[str, str | int]] = []
    for group in groups:  # type: GroupSchema
        stats.append(await handle_tg_group(**{
            "group": group,
            "api": api,
            "options": kwargs
        }))
    return stats


collect_functions_dict = {
    "vk": collect_vk_stats,
    "tg": collect_tg_stats,
}


async def collect_stats(**kwargs):
    platform = kwargs.get('platform')
    api: Optional[VkApiMethod | TelegramClient] = None
    match platform:
        case Platforms.VK:
            api = get_vk_api_session()
        case Platforms.TG:
            api = get_tg_api_session()
    if not api:
        raise ValueError('Произошла ошибка при получении объекта API')

    groups = await get_groups(platform.id)

    collect_func = collect_functions_dict.get(platform.alias, None)
    if not collect_func:
        raise ValueError('Неизвестная платформа')
    stats = await collect_func(api, groups, **kwargs)
    return stats
