from abc import ABC, abstractmethod


class Stat(ABC):

    @abstractmethod
    async def get_group(self):
        pass

    @abstractmethod
    async def get_main_info(self):
        pass

    @abstractmethod
    async def get_notes(self):
        pass

    @abstractmethod
    async def handle_batch(self, batch):
        pass

    @abstractmethod
    async def _update_top_posts(self, item, likes_count, comments_count, reposts_count, views_count):
        pass

    @abstractmethod
    async def prepare_object(self):
        pass

    @abstractmethod
    async def get_data(self):
        pass
