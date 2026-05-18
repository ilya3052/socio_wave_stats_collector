import logging
from datetime import timedelta, datetime, date, timezone
from typing import Any, Dict, Optional, Set
import re
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, InputChannel, ChatFull, Message, PeerChannel, MessageMediaPhoto, \
    MessageMediaDocument

from src.core import BATCH_SIZE, Type
from .StatABS import Stat

logger = logging.getLogger(__name__)


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

        self._posts_data = {}

        self._top_posts = {
            "most_liked": {
                "id": 0,
                "likes_count": 0
            },
            "most_reposted": {
                "id": 0,
                "reposts_count": 0
            },
            "most_commented": {
                "id": 0,
                "comms_count": 0
            },
            "most_viewed": {
                "id": 0,
                "views_count": 0
            }
        }

    async def get_group(self):
        self._channel = await self._api.get_entity(PeerChannel(self._group_id))
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
            _type = self._options.get('Type')

            if _type == Type.DAILY:
                offset = (datetime.now() - timedelta(days=1)).date()
                end_period = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif _type == Type.HOURLY:
                offset = (datetime.now() - timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
                end_period = datetime.now().replace(minute=0, second=0, microsecond=0)
            elif _type == Type.TOP:
                offset = (datetime.now() - timedelta(weeks=1)).date()
                end_period = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            async for msg in self._api.iter_messages(self._channel, reverse=True, offset_date=offset,
                                                     wait_time=1.2):  # type: Message

                msg_date = msg.date
                if msg_date.tzinfo is not None:
                    msg_date = msg_date.replace(tzinfo=None)

                if (offset and end_period) and msg_date >= end_period:
                    break

                if grouped_id := msg.grouped_id:
                    if grouped_id in self._seen_groups:
                        continue
                    self._seen_groups.add(msg.grouped_id)
                batch.append(msg)

                if len(batch) >= BATCH_SIZE:
                    print(f'handle batch {idx} by group {self._screen_name} (ID {self._group_id})')
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
            try:
                item_stats = await get_item_stats(item)

                views_count = item_stats[0]
                likes_count = item_stats[1]
                comms_count = item_stats[2]
                reposts_count = item_stats[3]
                has_photo = isinstance(item.media, MessageMediaPhoto)
                has_video = isinstance(item.media, MessageMediaDocument) and item.media.video

                self._posts_count += 1

                if self._options.get('Type') == Type.DAILY:
                    date = item.date
                    if item.date.tzinfo is not None:
                        date = item.date.replace(tzinfo=None) + timedelta(hours=3)
                    hour = date.hour
                    day_of_week = date.weekday()

                    text = item.message
                    text = re.sub(r'(\d)\s+(\d)', r'\1-\2', text)
                    text_clean = re.sub(r'[^\w\s-]', '', text)
                    self._posts_data[str(item.id)] = {
                        "likes_count": likes_count,
                        "comms_count": comms_count,
                        "reposts_count": reposts_count,
                        "views_count": views_count,
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "is_weekend": day_of_week >= 5,
                        "is_night": hour < 6 or hour >= 22,
                        "is_prime_time": 18 <= hour < 23,
                        "has_text": bool(getattr(item, 'text', None)),
                        "has_media": bool(item.media),
                        "text_length": len(item.message),

                        "is_morning": 6 <= hour < 10,
                        "is_lunch": 12 <= hour <= 14,
                        "like_view_ratio": likes_count / views_count,
                        "er": round(((likes_count + reposts_count + comms_count) / views_count), 4),
                        "has_video": has_video,
                        "has_photo": has_photo,
                        # "media_count": len(media),
                        "word_count": len(text_clean.split())
                    }

                if (_type := self._options.get('Type')) == Type.TOP:
                    await self._update_top_posts(item, likes_count, comms_count, reposts_count, views_count)
                    continue

                self._views += views_count
                self._likes_count += likes_count
                self._comments_count += comms_count
                self._repost_count += reposts_count
            except Exception as e:
                post_id = item.id or 'unknown'
                logger.warning(
                    f"Ошибка обработки записи {post_id} в группе TG {self._group_id}: {e}",
                )
                continue
        return True

    async def _update_top_posts(self, item: Message, likes_count, comments_count, reposts_count, views_count):
        if likes_count >= self._top_posts.get('most_liked').get('likes_count'):
            self._top_posts['most_liked'] = {
                "id": item.id,
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.message[:150]
            }
        if reposts_count >= self._top_posts.get('most_reposted').get('reposts_count'):
            self._top_posts['most_reposted'] = {
                "id": item.id,
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.message[:150]
            }
        if comments_count >= self._top_posts.get('most_commented').get('comms_count'):
            self._top_posts['most_commented'] = {
                "id": item.id,
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.message[:150]
            }
        if views_count >= self._top_posts.get('most_viewed').get('views_count'):
            self._top_posts['most_viewed'] = {
                "id": item.id,
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.message[:150]
            }

    async def get_service_data(self):
        return self._posts_count

    async def get_data(self):
        if (_type := self._options.get('Type')) == Type.TOP:
            return {
                "Название группы": self._name,
                "External ID": self._group_id,
                "Количество записей": self._posts_count,
                'screen_name': self._screen_name,
                'top_posts': self._top_posts
            }
        data = {
            "Название группы": self._name,
            "External ID": self._group_id,
            "Подписчики": self._participants_count,
            "Лайки": self._likes_count,
            "Комментарии": self._comments_count,
            "Репосты": self._repost_count,
            "Просмотры": self._views,
            "Количество записей": self._posts_count,
            "screen_name": self._screen_name
        }
        if _type == Type.DAILY:
            data['additional_data'] = self._posts_data

        return data

    async def prepare_object(self):
        if not await self.get_group():
            return False
        if not await self.get_main_info():
            return False
        if not await self.get_notes():
            return False
        return True
