from datetime import datetime
from typing import Dict

from src.exceptions import GroupHandleError
from src.platformStats import TGStat


async def handle_tg_group(api, group, **kwargs):
    options = kwargs.get('options')

    stat = TGStat(api=api, group_id=group.external_id, **options)

    start = datetime.now()
    if not await stat.prepare_object():
        raise GroupHandleError(f'Произошла ошибка при обработке группы {group.name} на платформе TG')
    now = datetime.now()

    posts_count = await stat.get_service_data()

    print(f'Время полной обработки с запросами - {(now - start).total_seconds()} c.\n'
          f'Обработано записей: {posts_count}')

    data: Dict[str, str | int] = await stat.get_data()
    if not data:
        raise ValueError(f'Произошла ошибка при получении данных для группы {group.name} на платформе TG')
    data['Internal ID'] = group.id
    return data

