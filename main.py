import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.stats import collect_stats, handle_stats

import asyncio

from datetime import datetime

from src.core import Session, Type, create_tables

from src.models import GroupSchema, GroupModel, PlatformSchema, \
    PlatformModel, ServiceAccountSchema, ServiceAccountModel
from src.repositories import GroupsRepository, PlatformRepository, ServiceAccountRepository


async def main(_type):
    # create_tables()

    options = {_type: True}

    stats = await collect_stats(**options)
    await handle_stats(stats, Type(_type))


if __name__ == "__main__":
    _type = sys.argv[1].lstrip('-')

    asyncio.run(main(_type))


async def create_basic_elem():
    with Session() as session:
        repo = PlatformRepository(session)
        platform = PlatformSchema(**{
            "platform_id": 1,
            "platform_name": "ВКонтакте"
        })
        repo.add(PlatformModel(**platform.model_dump()))

        repo = ServiceAccountRepository(session)
        sacc = ServiceAccountSchema(**{
            "serviceAccount_id": 1,
            "serviceAccount_link": 'https://link.ru',
            "serviceAccount_name": 'SocialPulse',
            "platform_id": 1
        })
        repo.add(ServiceAccountModel(**sacc.model_dump()))

        repo = GroupsRepository(session)
        group = GroupSchema(**{
            "group_id": 1,
            "group_externalID": 114911631,
            "group_name": "Липецкий Политех (ЛГТУ)",
            "group_link": "https://vk.ru/infolgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 1,
            "platform_id": 1
        })
        repo.add(GroupModel(**group.model_dump()))
