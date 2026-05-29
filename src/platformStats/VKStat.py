import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from icecream import ic
from vk_api.vk_api import VkApiMethod

from src.core import BATCH_SIZE, Type
from .StatABS import Stat
import re
logger = logging.getLogger(__name__)


async def _cut_off_excess_part(_type, batch):
    new_batch = []
    if _type == Type.DAILY:
        for item in batch:
            publication_date = item.get('date')
            date: datetime = datetime.fromtimestamp(publication_date)
            if date.date() == (datetime.today() - timedelta(days=1)).date():
                new_batch.append(item)
    elif _type == Type.HOURLY:
        for item in batch:
            publication_date = item.get('date')
            date: datetime = datetime.fromtimestamp(publication_date)
            if date >= datetime.now() - timedelta(hours=2):
                new_batch.append(item)
    elif _type == Type.TOP:
        for item in batch:
            publication_date = item.get('date')
            date: datetime = datetime.fromtimestamp(publication_date)
            if date >= datetime.now() - timedelta(weeks=1):
                new_batch.append(item)
    return new_batch


class VKStat(Stat):
    def __init__(self, api, group_id, **options):

        self._options: Dict[str, Any] = options

        self._api: VkApiMethod = api
        self._group_id = group_id
        self._group: Optional[Dict[str, str | int]] = None

        self._participants_count = 0
        self._likes_count = 0
        self._comments_count = 0
        self._repost_count = 0
        self._views = 0

        self._screen_name = None
        self._name = None

        self._time_for_handle = timedelta()
        self._posts_count = 0

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

        self._posts_data = {}

    async def get_group(self):
        loop = asyncio.get_event_loop()
        groups = await loop.run_in_executor(
            None, lambda: self._api.groups.getById(group_id=self._group_id, extended=1, fields="members_count")
        )
        if not groups:
            return False
        self._group = groups[0]
        self._name = self._group.get('name')
        return True

    async def get_main_info(self):
        if not self._group:
            return False

        self._participants_count = self._group.get("members_count")
        self._screen_name = self._group.get('screen_name')
        return True

    async def get_notes(self):
        try:
            offset = 0
            must_stop = False
            idx = 1
            loop = asyncio.get_event_loop()

            while not must_stop:
                items = await loop.run_in_executor(
                    None,
                    lambda: self._api.wall.get(domain=self._screen_name, offset=offset, count=BATCH_SIZE).get("items")
                )

                if (_type := self._options.get('Type')) != Type.ABSOLUTE:
                    items = await _cut_off_excess_part(_type, items)
                    if len(items) < BATCH_SIZE:
                        must_stop = True

                if not items:
                    break
                print(f'handle batch {idx} by group {self._screen_name} (ID {self._group_id})')
                if not await self.handle_batch(items):
                    return False

                idx += 1
                offset += BATCH_SIZE

            return True

        except Exception as E:
            print(E)
            print(E.__class__.__name__)
            return False

    async def handle_batch(self, batch):
        for item in batch:  # type: Dict
            if item.get('is_pinned', False):
                continue

            try:
                self._posts_count += 1

                likes_count = item.get('likes', {}).get('count', 0)
                comms_count = item.get("comments", {}).get('count', 0)
                reposts_count = item.get("reposts", {}).get('count', 0)
                views_count = item.get("views", {}).get('count', 0)

                media = item.get('attachments')
                has_video = False
                has_photo = False
                for m in media:
                    if m.get('type') == 'photo' and not has_photo:
                        has_photo = True
                        continue
                    if m.get('type') == 'video' and not has_video:
                        has_video = True
                        continue

                if self._options.get('Type') == Type.DAILY:
                    date = item.get('date')
                    hour = datetime.fromtimestamp(date).hour
                    day_of_week = datetime.fromtimestamp(date).weekday()

                    text = item.get('text')
                    text = re.sub(r'(\d)\s+(\d)', r'\1-\2', text)
                    text_clean = re.sub(r'[^\w\s-]', '', text)

                    self._posts_data[str(item.get('id'))] = {
                        "likes_count": likes_count,
                        "comms_count": comms_count,
                        "reposts_count": reposts_count,
                        "views_count": views_count,
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "is_weekend": day_of_week >= 5,
                        "text_length": len(text),

                        "like_view_ratio": likes_count / views_count,
                        "has_video": has_video,
                        "has_photo": has_photo,
                        "word_count": len(text_clean.split())
                    }

                if (_type := self._options.get('Type')) == Type.TOP:
                    await self._update_top_posts(item, likes_count, comms_count, reposts_count, views_count)
                    continue

                self._comments_count += comms_count
                self._likes_count += likes_count
                self._repost_count += reposts_count
                self._views += views_count

            except Exception as e:
                post_id = item.get('id', 'unknown')
                logger.warning(
                    f"Ошибка обработки поста {post_id} в группе VK {self._group_id}: {e}")
                continue

        return True

    async def _update_top_posts(self, item, likes_count, comments_count, reposts_count, views_count):
        if likes_count >= self._top_posts.get('most_liked').get('likes_count'):
            self._top_posts['most_liked'] = {
                "id": item.get('id'),
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.get('text')[:150]
            }
        if comments_count >= self._top_posts.get('most_reposted').get('reposts_count'):
            self._top_posts['most_reposted'] = {
                "id": item.get('id'),
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.get('text')[:150]
            }
        if reposts_count >= self._top_posts.get('most_commented').get('comms_count'):
            self._top_posts['most_commented'] = {
                "id": item.get('id'),
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.get('text')[:150]
            }
        if views_count >= self._top_posts.get('most_viewed').get('views_count'):
            self._top_posts['most_viewed'] = {
                "id": item.get('id'),
                "likes_count": likes_count,
                "comms_count": comments_count,
                "reposts_count": reposts_count,
                "views_count": views_count,
                "content": item.get('text')[:150]
            }

    async def get_data(self):
        if (_type := self._options.get('Type')) == Type.TOP:
            return {
                "External ID": self._group_id,
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

    async def get_service_data(self):
        return self._posts_count
