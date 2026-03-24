import asyncio
from datetime import datetime
from typing import Dict

from icecream import ic
from pydantic import ValidationError

from models import GroupSchema, AbsoluteStatsSchema
from stats import VKStat
from core.apiVK import get_vk_api_session


async def main():
    vk_api = get_vk_api_session()
    stat = VKStat(api=vk_api, group_id=114911631)
    start = datetime.now()
    await stat.prepare_object()
    now = datetime.now()
    time, posts_count, _time = await stat.get_service_data()
    print(f'Время обработки записей - {time} с.\n'
          f'Время полной обработки с запросами - {(now - start).total_seconds()} c.\n'
          f'Обработано записей: {posts_count}')
    ic(_time, sum(_time) / len(_time), sum(_time), len(_time))

    data: Dict[str, str | int] = await stat.get_data()
    print(data)

    try:
        group_schema = GroupSchema(**{
            "group_id": data.get('ID'),
            "group_name": data.get('Название группы'),
            "group_link": f"https://vk.ru/{data.get('screen_name')}",
            "serviceAccount_id": 1,
            "platform_id": 1
        })
        abs_stats_schema = AbsoluteStatsSchema(**{
            "absoluteStats_id": 1,
            "absoluteStats_likesCount": data.get('Лайки'),
            "absoluteStats_viewsCount": data.get('Просмотры'),
            "absoluteStats_participantsCount": data.get('Подписчики'),
            "absoluteStats_repostCount": data.get('Репосты'),
            "absoluteStats_commsCount": data.get('Комментарии'),
            "absoluteStats_coverage": 1,
            "group_id": data.get('ID')
        })
        print(group_schema.model_dump())
        print(group_schema.model_dump_json())
        print(abs_stats_schema.model_dump())
        print(abs_stats_schema.model_dump_json())
    except ValidationError as VE:
        print(VE)
    # group.pop()



if __name__ == "__main__":
    asyncio.run(main())
