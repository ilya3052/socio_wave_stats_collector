import os
import sys

from src.core.apiTG import get_tg_api_session
from src.core.config import Platforms

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.stats import collect_stats, handle_stats

import asyncio

from datetime import datetime

from src.core import Session, Type, create_tables

from src.models import GroupSchema, GroupModel, PlatformSchema, \
    PlatformModel, ServiceAccountSchema, ServiceAccountModel
from src.repositories import GroupsRepository, PlatformRepository, ServiceAccountRepository


async def main(platform, _type):
    try:
        _platform = Platforms(platform)
        stats_type = Type(_type)
        options = {'platform': Platforms(platform), 'Type': stats_type}
        if _platform == Platforms.TG:
            api = get_tg_api_session()
            options['api'] = api
            async with api:
                stats = await collect_stats(**options)

        elif _platform == Platforms.VK:
            options = {'platform': Platforms(platform), 'Type': stats_type}
            stats = await collect_stats(**options)

        if not await handle_stats(stats, stats_type):
            print('Произошла неизвестная ошибка')

    except ValueError as VE:
        print(VE)


async def create_basic_elem():
    create_tables()
    with Session() as session:
        repo = PlatformRepository(session)
        platform_vk = PlatformSchema(**{
            "platform_id": 1,
            "platform_name": "ВКонтакте"
        })
        platform_tg = PlatformSchema(**{
            "platform_id": 2,
            "platform_name": "Телеграм"
        })

        repo.add(PlatformModel(**platform_vk.model_dump()))
        repo.add(PlatformModel(**platform_tg.model_dump()))
        repo.commit()

        repo = ServiceAccountRepository(session)
        sacc_vk = ServiceAccountSchema(**{
            "serviceAccount_id": 1,
            "serviceAccount_link": 'https://link.ru',
            "serviceAccount_name": 'SocialPulse',
            "platform_id": 1
        })
        sacc_tg = ServiceAccountSchema(**{
            "serviceAccount_id": 2,
            "serviceAccount_link": 'https://link.ru',
            "serviceAccount_name": 'SocialPulse',
            "platform_id": 2
        })
        repo.add(ServiceAccountModel(**sacc_vk.model_dump()))
        repo.add(ServiceAccountModel(**sacc_tg.model_dump()))
        repo.commit()

        repo = GroupsRepository(session)
        group_vk = GroupSchema(**{
            "group_id": 1,
            "group_externalID": 114911631,
            "group_name": "Липецкий Политех (ЛГТУ)",
            "group_link": "https://vk.ru/infolgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 1,
            "platform_id": 1
        })
        group_tg = GroupSchema(**{
            "group_id": 2,
            "group_externalID": 1397484238,
            "group_name": "Липецкий Политех (ЛГТУ)",
            "group_link": "https://t.me/infolgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 2,
            "platform_id": 2
        })
        repo.add(GroupModel(**group_vk.model_dump()))
        repo.add(GroupModel(**group_tg.model_dump()))
        repo.commit()


def print_help():
    print("""\
ИСПОЛЬЗОВАНИЕ
    main.py <command> [options]
КОМАНДЫ
    vk             Сбор статистики групп ВКонтакте
    tg              Сбор статистики каналов Телеграм
ОПЦИИ
    --absolute         Сбор полной статистики группы
    --daily            Сбор статистики за последние сутки
    --hourly          Сбор статистики за последние два часа
    -ct --create-tables   Создание таблиц в базе
    -h --help             Показать эту подсказку
ПРИМЕРЫ       
    main.py vkontakte -a
    main.py --create-tables
    """)


if __name__ == "__main__":
    if len(sys.argv) == 1 or (sys.argv[1].lstrip('-')) in ('h', 'help'):
        print_help()
        exit(0)

    # command, param = sys.argv[1].lstrip('-'), sys.argv[2].lstrip('-')

    if sys.argv[1].lstrip('-') in ('create-tables', 'ct'):
        asyncio.run(create_basic_elem())
    else:
        asyncio.run(main(sys.argv[1], sys.argv[2].lstrip('-')))
