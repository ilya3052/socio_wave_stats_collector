import asyncio
import os
from enum import Enum
from typing import Union

import aio_pika
from aio_pika.exceptions import ChannelInvalidStateError
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

KEY = os.getenv('ENCRYPTION_KEY')

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

SPECIAL_VK_ACC_SERVICE_KEY = os.getenv("SPECIAL_VK_ACC_SERVICE_KEY")
SPECIAL_TG_ACC_SESSION_PATH = os.getenv("SPECIAL_TG_ACC_SESSION_PATH")

BATCH_SIZE = 100


class Type(Enum):
    DAILY = 'daily'
    HOURLY = 'hourly'
    TOP = 'top'
    ABSOLUTE = 'absolute'


class BestPostInfoType(Enum):
    MOST_LIKED = 'most_liked'
    MOST_REPOSTED = 'most_reposted'
    MOST_COMMENTED = 'most_commented'
    MOST_VIEWED = 'most_viewed'


class SnapshotType(Enum):
    HOURLY = Type.HOURLY
    DAILY = Type.DAILY


class Platforms(Enum):
    VK = (1, 'vk')
    TG = (2, 'tg')

    def __init__(self, code: int, alias: str):
        self.code = code
        self.alias = alias

    @classmethod
    def _missing_(cls, value: Union[int, str]):
        if isinstance(value, str):
            val = value.strip().lower()
            for member in cls:
                if member.alias == val:
                    return member
        if isinstance(value, int):
            return cls._value2member_map_.get(value)
        raise ValueError(f"{value} некорректный параметр для {cls.__name__}")

    @property
    def id(self) -> int:
        return self.code

    @property
    def name(self) -> str:
        return self.alias

    def __int__(self) -> int:
        return self.code


_connection: aio_pika.abc.AbstractRobustConnection | None = None
_channel: aio_pika.abc.AbstractChannel | None = None
_lock = asyncio.Lock()


async def get_channel() -> aio_pika.abc.AbstractChannel:
    global _connection, _channel

    async with _lock:
        if _connection is None or _connection.is_closed:
            _connection = await aio_pika.connect_robust(
                RABBITMQ_URL, heartbeat=60,
            )
            _channel = None

        if _channel is None or _channel.is_closed:
            try:
                _channel = await _connection.channel()
            except ChannelInvalidStateError:
                _channel = None
                _connection = None
                return await get_channel()
    return _channel


async def close_rabbitmq():
    global _connection, _channel
    async with _lock:
        if _channel is not None and not _channel.is_closed:
            await _channel.close()
            _channel = None
        if _connection is not None and not _connection.is_closed:
            await _connection.close()
            _connection = None
