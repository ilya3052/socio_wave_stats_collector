from datetime import timedelta, datetime, date, timezone
from typing import Any, Dict, Optional, Set

from icecream import ic
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, InputChannel, ChatFull, Message

from src.core.config import BATCH_SIZE, Type
from src.platformStats.StatABS import Stat


async def get_item_stats(msg):
    reactions_count, repost_count, replies_count = 0, 0, 0
    views_count = msg.views if msg.views else 0
    if reactions := msg.reactions:
        for result in reactions.results:
            reactions_count += result.count

    repost_count += msg.forwards if msg.forwards else 0

    if replies := msg.replies:
        replies_count += replies.replies if replies.replies else 0
    return views_count, reactions_count, replies_count, repost_count


class TGStat(Stat):
    def __init__(self, api, group_id, **options):
        self._options: Dict[str, Any] = options
        self._api: TelegramClient = api
        self._group_id = group_id

        self._channel: Optional[Channel] = None
        self._input_channel: Optional[InputChannel] = None
        self._chat_info: Optional[ChatFull] = None

        self._participants_count = 0
        self._likes_count = 0
        self._comments_count = 0
        self._repost_count = 0
        self._views = 0

        self._screen_name = None
        self._name = None

        self._seen_groups: Set = set()
        self._posts_count = 0

    async def get_group(self):
        self._channel = await self._api.get_entity(self._group_id)
        self._input_channel = InputChannel(self._channel.id, self._channel.access_hash)
        return True

    async def get_main_info(self):
        if not self._channel or not self._input_channel:
            return False

        self._chat_info = await self._api(GetFullChannelRequest(self._input_channel))
        self._name = self._channel.title
        self._screen_name = self._channel.username
        self._participants_count = self._chat_info.full_chat.participants_count
        return True

    async def get_notes(self):
        try:
            batch = []

            idx = 1

            offset: Optional[datetime | date | timedelta] = None
            end_period: Optional[datetime | date] = None
            limit = None
            if (_type := self._options.get('Type')) == Type.DAILY:
                offset = (datetime.now(timezone.utc) - timedelta(days=1)).date()
                end_period = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                limit = BATCH_SIZE
            elif _type == Type.HOURLY:
                offset = (datetime.now(timezone.utc) - timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
                end_period = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
                limit = BATCH_SIZE

            async for msg in self._api.iter_messages(self._channel, limit=limit, reverse=True, offset_date=offset, wait_time=1.0):  # type: Message
                if (offset and end_period) and msg.date >= end_period:
                    break

                if grouped_id := msg.grouped_id:
                    if grouped_id in self._seen_groups:
                        continue
                    self._seen_groups.add(msg.grouped_id)
                batch.append(msg)

                if len(batch) >= BATCH_SIZE:
                    print(f'handle batch {idx}')
                    if not await self.handle_batch(batch):
                        return False
                    idx += 1
                    batch.clear()

            if batch:
                if not await self.handle_batch(batch):
                    return False
                batch.clear()
            return True
        except Exception as E:
            print(E)
            print(E.__class__.__name__)
            return False

    async def handle_batch(self, batch):
        for item in batch:  # type: Message
            if not isinstance(item, Message):
                continue

            item_stats = await get_item_stats(item)

            self._posts_count += 1
            self._views += item_stats[0]
            self._likes_count += item_stats[1]
            self._comments_count += item_stats[2]
            self._repost_count += item_stats[3]
        return True

    async def get_service_data(self):
        return self._posts_count

    async def get_data(self):
        return {
            "Название группы": self._name,
            "External ID": self._group_id,
            "Подписчики": self._participants_count,
            "Лайки": self._likes_count,
            "Комментарии": self._comments_count,
            "Репосты": self._repost_count,
            "Просмотры": self._views,
            'screen_name': self._screen_name
        }

    async def prepare_object(self):
        if not await self.get_group():
            return False
        if not await self.get_main_info():
            return False
        if not await self.get_notes():
            return False
        return True
