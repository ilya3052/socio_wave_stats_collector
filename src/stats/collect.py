import logging
from typing import List, Dict

from src.core import Platforms
from src.exceptions import GroupHandleError, NoRecordsFound
from src.handlers import handle_vk_group, handle_tg_group
from src.models import GroupSchema

logger = logging.getLogger(__name__)


async def collect_vk_stats(api, groups, **options):
    try:
        stats: List[Dict[str, str | int] | Exception] = []
        for group in groups:  # type: GroupSchema
            logger.info(f"Старт обработки VK группы с ID {group.id} ({group.name}) (ID в VK {group.external_id})")
            try:
                group_stats = await handle_vk_group(api, group, **options)
            except NoRecordsFound as NRF:
                logger.warning(f"Группа VK '{group.name}' пропущена - нет записей за период")
                stats.append(NRF)
                continue
            except GroupHandleError as GHE:
                # TODO: сделать отправку уведомления для админа
                logger.error(
                    f"Сбор статистики для группы '{group.name}' (VK) упал с ошибкой: {GHE}. Подробнее см. в логах")
                stats.append(GHE)
                continue
            stats.append(group_stats)
            logger.info(f"VK группа '{group.name}' успешно обработана")
        return stats
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Неожиданная ошибка в collect_vk_stats")
        raise


async def collect_tg_stats(api, groups, **options):
    try:
        stats: List[Dict[str, str | int] | Exception] = []
        for group in groups:  # type: GroupSchema
            logger.info(f"Старт обработки TG группы с ID {group.id} ({group.name}) (ID в TG {group.external_id})")
            try:
                group_stats = await handle_tg_group(api, group, **options)
            except NoRecordsFound as NRF:
                logger.warning(f"Группа TG '{group.name}' пропущена - нет записей за период")
                stats.append(NRF)
                continue
            except GroupHandleError as GHE:
                # TODO: сделать отправку уведомления для админа
                logger.error(
                    f"Сбор статистики для группы '{group.name}' (TG) упал с ошибкой: {GHE}. Подробнее см. в логах")
                stats.append(GHE)
                continue
            stats.append(group_stats)
            logger.info(f"TG группа '{group.name}' успешно обработана")
        return stats
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Неожиданная ошибка в collect_tg_stats")
        raise


collect_functions_dict = {
    "vk": collect_vk_stats,
    "tg": collect_tg_stats,
}


async def collect_stats(groups, api, platform, **options):
    try:
        collect_func = collect_functions_dict.get(platform.alias)
        if not collect_func:
            logger.error(f"Неизвестная платформа: {platform.alias}")
            raise ValueError('Неизвестная платформа')

        logger.info(f"Запущен сбор статистики для платформы {platform.alias.upper()} ({len(groups)} групп)")

        stats = None

        if platform == Platforms.VK:
            stats = await collect_func(api, groups, **options)
        elif platform == Platforms.TG:
            async with api:
                stats = await collect_func(api, groups, **options)

        if not stats:
            logger.error(f"collect_func вернула пустой результат для {platform.alias}")
            # raise ValueError('Ошибка при получении данных статистики')

        logger.info(f"Успешно собрана статистика для {len(stats)} групп на платформе {platform.alias.upper()}")
        return stats

    except ValueError:
        raise
    except Exception as e:
        logger.exception(f"Критическая ошибка в collect_stats для платформы {platform.alias}")
        raise
