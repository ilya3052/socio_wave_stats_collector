from typing import Optional, List, Dict

from src.core import Session, Platforms, get_vk_api_session
from src.handlers import handle_vk_group, handle_tg_group
from src.models import GroupSchema
from src.repositories import GroupsRepository


async def get_groups():
    groups: Optional[List[GroupSchema]] = None

    with Session() as session:
        repo = GroupsRepository(session)
        groups: List[GroupSchema] = [GroupSchema.model_validate(group) for group in repo.get_all()]

    return groups


async def create_apis():
    api_vk = get_vk_api_session()
    api_tg = None
    return api_vk, api_tg


async def collect_stats(**kwargs):
    vk_api, tg_api = await create_apis()
    groups = await get_groups()
    options = kwargs

    stats: Optional[Dict[str, str | int]] = None
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


    return stats
