import os
from enum import Enum
from typing import Union

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

KEY = os.getenv('ENCRYPTION_KEY')

BATCH_SIZE = 100


class Type(Enum):
    DAILY = 'daily'
    HOURLY = 'hourly'
    ABSOLUTE = 'absolute'


class SnapshotType(Enum):
    HOURLY = Type.HOURLY
    DAILY = Type.DAILY


class Platforms(Enum):
    VK = (2, 'vk')
    TG = (1, 'tg')

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
