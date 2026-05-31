import json

from aio_pika.abc import AbstractIncomingMessage

from src.api.apiTG import get_tg_api_session
from src.api.apiVK import get_vk_api_session
from src.core import Session, get_channel, Platforms, SPECIAL_VK_ACC_SERVICE_KEY, SPECIAL_TG_ACC_SESSION_PATH, Type
from src.models import GroupModel
from src.repositories import GroupsRepository
from src.stats import collect_stats, send_absolute_stats_to_db


def get_api(platform):
    api = None
    if platform == Platforms.TG:
        api = get_tg_api_session(SPECIAL_TG_ACC_SESSION_PATH)
    elif platform == Platforms.VK:
        api = get_vk_api_session(SPECIAL_VK_ACC_SERVICE_KEY)
    return api


async def process_message(message: AbstractIncomingMessage):
    async with message.process():
        body = message.body
        group_data = json.loads(body)
        with Session() as session:
            group_repo = GroupsRepository(session)
            group: GroupModel = group_repo.get(group_data.get('group_id'))
            group.status = 'COLLECTING'
            session.commit()
        platform = Platforms(group.platform.alias)
        api = get_api(platform)
        stats = await collect_stats(api=api, groups=[group], platform=platform, **{'Type': Type.ABSOLUTE})
        await send_absolute_stats_to_db(stats[0])


async def start_consumer():
    channel = await get_channel()
    queue = await channel.declare_queue("abs-stats", durable=True)
    await channel.set_qos(prefetch_count=1)
    await queue.consume(process_message)
