import logging
from datetime import datetime
from typing import Dict

from src.core import Type
from src.exceptions import GroupHandleError, NoRecordsFound
from src.platformStats import TGStat

logger = logging.getLogger(__name__)


async def handle_tg_group(api, group, **options):
    stat = TGStat(api=api, group_id=group.external_id, **options)

    start = datetime.now()
    try:
        if not await stat.prepare_object():
            raise GroupHandleError(f'Не удалось подготовить объект группы {group.name} (TG)')
        if await stat.get_service_data() == 0 and options.get('Type') == Type.TOP:
            raise NoRecordsFound(
                f"Для группы {group.name} (TG) за последнюю неделю не найдено ни одной записи, пропускаем")
    except NoRecordsFound:
        raise
    except Exception as e:
        logger.exception(f"Критическая ошибка обработки группы TG {group.name} с ID {group.external_id}")
        raise GroupHandleError(f'Произошла ошибка при обработке группы {group.name} на платформе TG') from e
    now = datetime.now()

    service_data = await stat.get_service_data()

    logger.info(
        f"TG группа '{group.name}' обработана за {(now - start).total_seconds():.2f} сек. Обработано записей: {service_data.get('posts_count')}",
    )

    data: Dict[str, str | int] = await stat.get_data()
    if not data:
        raise ValueError(f'Произошла ошибка при получении данных для группы {group.name} на платформе TG')
    data['Internal ID'] = group.id
    data['service_data'] = service_data
    return data
