import logging
from datetime import datetime
from typing import Dict

from src.exceptions import GroupHandleError
from src.platformStats import VKStat

logger = logging.getLogger(__name__)


async def handle_vk_group(api, group, **options):
    stat = VKStat(api=api, group_id=group.external_id, **options)

    start = datetime.now()
    try:
        if not await stat.prepare_object():
            raise GroupHandleError(f'Не удалось подготовить объект группы {group.name} (VK)')
        if await stat.get_service_data() == 0 and options.get('Type') == Type.TOP:
            raise NoRecordsFound(
                f"Для группы {group.name} (VK) за последнюю неделю не найдено ни одной записи, пропускаем")
    except NoRecordsFound:
        raise
    except Exception as e:
        logger.exception(f"Критическая ошибка обработки группы TG {group.name} с ID {group.external_id}")
        raise GroupHandleError(f'Произошла ошибка при обработке группы {group.name} на платформе TG') from e
    now = datetime.now()

    posts_count = await stat.get_service_data()

    logger.info(
        f"VK группа '{group.name}' обработана за {(now - start).total_seconds():.2f} сек. Обработано записей: {posts_count}",
    )

    data: Dict[str, str | int] = await stat.get_data()
    if not data:
        raise ValueError(f'Произошла ошибка при получении данных для группы {group.name} на платформе ВК')
    data['Internal ID'] = group.id
    return data
