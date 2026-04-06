from typing import List, Dict

from src.core import Platforms
from src.exceptions import GroupHandleError
from src.handlers import handle_vk_group, handle_tg_group
from src.models import GroupSchema


async def collect_vk_stats(api, groups, **kwargs):
    try:
        stats: List[Dict[str, str | int]] = []
        for group in groups:  # type: GroupSchema
            stats.append(await handle_vk_group(api, group, **{
                "options": kwargs
            }))
        return stats
    except GroupHandleError:
        raise
    except ValueError:
        raise


async def collect_tg_stats(api, groups, **kwargs):
    try:
        stats: List[Dict[str, str | int]] = []
        for group in groups:  # type: GroupSchema
            stats.append(await handle_tg_group(api, group, **{
                "options": kwargs
            }))
        return stats
    except GroupHandleError:
        raise
    except ValueError:
        raise


collect_functions_dict = {
    "vk": collect_vk_stats,
    "tg": collect_tg_stats,
}


async def collect_stats(groups, api, platform, **kwargs):
    try:
        collect_func = collect_functions_dict.get(platform.alias, None)
        if not collect_func:
            raise ValueError('Неизвестная платформа')
        if platform == Platforms.VK:
            stats = await collect_func(api, groups, **kwargs)
        elif platform == Platforms.TG:
            async with api:
                stats = await collect_func(api, groups, **kwargs)

        if not stats:
            raise ValueError('Ошибка при получении данных статисики')

        return stats
    except ValueError:
        raise
    except GroupHandleError:
        raise
