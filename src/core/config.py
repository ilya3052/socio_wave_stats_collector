import os
from enum import Enum, IntEnum
from typing import Union

from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("SERVICE_KEY")
PROTECTED_KEY = os.getenv("PROTECTED_KEY")
APP_ID = os.getenv("APP_ID")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
# TOKEN = os.getenv("BOT_TOKEN")

SESSION_PATH = "../sessions/anon.session"

BATCH_SIZE = 100


class Type(Enum):
    DAILY = 'daily'
    HOURLY = 'hourly'
    ABSOLUTE = 'absolute'


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

    def __int__(self) -> int:
        return self.code
