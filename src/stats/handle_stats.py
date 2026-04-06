from src.core import Type
from .send import send_daily_stats_to_db, send_absolute_stats_to_db


async def handle_stats(stats, stats_type):
    match stats_type:
        case Type.DAILY | Type.HOURLY:
            if not await send_daily_stats_to_db(stats, stats_type):
                return False
        case Type.ABSOLUTE:
            if not await send_absolute_stats_to_db(stats):
                return False
    return True
