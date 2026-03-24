from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List

from icecream import ic
from vk_api.vk_api import VkApiMethod

from core.config import BATCH_SIZE
from exceptions import LastPostException
from .StatABS import Stat


class VKStat(Stat):

    def __init__(self, api, group_id, last_post_id=1):
        self._api: VkApiMethod = api
        self._group_id = group_id
        self._last_post_id = last_post_id
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
        self._time = []

    async def get_group(self):
        groups = self._api.groups.getById(group_id=self._group_id, extended=1, fields="members_count")
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
            flag = False
            idx = 1
            while True:
                start = datetime.now()
                items = self._api.wall.get(domain=self._screen_name, offset=offset, count=BATCH_SIZE).get(
                    "items")  # type: List
                self._time.append((datetime.now() - start).total_seconds())
                if not items:
                    break
                try:
                    print(f'handle batch {idx}\nsize - {len(items)}')
                    start = datetime.now()
                    if not await self.handle_batch(items):
                        return False
                    now = datetime.now()
                    # print(f'Время на обработку - {now - start}')
                    self._time_for_handle += (now - start)

                    idx += 1
                except LastPostException:
                    flag = True
                if flag:
                    break
                offset += BATCH_SIZE
            return True

        except Exception as E:
            print(E)
            print(E.__class__.__name__)
            return False

    async def handle_batch(self, batch):
        for item in batch:  # type: Dict
            if item.get('id') == self._last_post_id:
                raise LastPostException

            if item.get('is_pinned', False):
                continue

            self._posts_count += 1

            likes = item.get('likes', None)
            if not likes:
                return False
            likes_count = likes.get('count', 0)

            comments = item.get("comments", None)
            if not comments:
                return False
            comments_count = comments.get('count', 0)

            reposts = item.get("reposts", None)
            if not reposts:
                return False
            reposts_count = reposts.get('count', 0)

            views = item.get("views", None)
            if not views:
                return False
            views_count = views.get('count', 0)

            self._comments_count += comments_count
            self._likes_count += likes_count
            self._repost_count += reposts_count
            self._views += views_count

        return True

    async def get_data(self):
        return {
            "Название группы": self._name,
            "ID": self._group_id,
            "Подписчики": self._participants_count,
            "Лайки": self._likes_count,
            "Комментарии": self._comments_count,
            "Репосты": self._repost_count,
            "Просмотры": self._views,
        }

    async def prepare_object(self):
        if not await self.get_group():
            return False
        if not await self.get_main_info():
            return False
        if not await self.get_notes():
            return False
        return True

    async def get_service_data(self):
        return self._time_for_handle, self._posts_count, self._time
