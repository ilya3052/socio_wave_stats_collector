import os
from enum import Enum, IntEnum

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


class SnapshotType(IntEnum):
    HOURLY = 0
    DAILY = 1


class Platforms(IntEnum):
    VK = 1
    TG = 2
