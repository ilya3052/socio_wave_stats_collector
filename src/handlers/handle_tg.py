from datetime import datetime
from typing import Dict

from src.models import GroupSchema
from src.platformStats.TGStat import TGStat


async def handle_tg_group(**kwargs):
    api = kwargs.get('api')
    options = kwargs.get('options')
    group: GroupSchema = kwargs.get('group')

    stat = TGStat(api=api, group_id=group.external_id, **options)
    start = datetime.now()
    await stat.prepare_object()
    now = datetime.now()
    posts_count = await stat.get_service_data()

    print(f'Время полной обработки с запросами - {(now - start).total_seconds()} c.\n'
          f'Обработано записей: {posts_count}')
    data: Dict[str, str | int] = await stat.get_data()
    data['Internal ID'] = group.id
    return data
