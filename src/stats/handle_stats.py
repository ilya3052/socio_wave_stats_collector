from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.core import Type
from .send import send_stats_to_db, send_absolute_stats_to_db
import logging

logger = logging.getLogger(__name__)


async def handle_stats(stats, stats_type):
    try:
        logger.info(f"Начало отправки статистики в БД (тип {stats_type}, ID группы {stats.get('Internal ID', 'unknown')})")

        match stats_type:
            case Type.DAILY | Type.HOURLY:
                if not await send_stats_to_db(stats, stats_type):
                    logger.error(f"send_stats_to_db вернула False для группы {stats.get('Internal ID')}")
                    return False
            case Type.ABSOLUTE:
                if not await send_absolute_stats_to_db(stats):
                    logger.error(f"send_absolute_stats_to_db вернула False для группы {stats.get('Internal ID')}")
                    return False
            case _:
                logger.error(f"Неизвестный тип снапшота: {stats_type}")
                raise ValueError('Неизвестный тип снапшота')

        logger.info(f"Статистика успешно обработана и сохранена (тип {stats_type}, ID группы {stats.get('Internal ID', 'unknown')})")
        return True

    except ValidationError:
        raise
    except NoResultFound:
        raise
    except Exception as e:
        logger.exception(f"Неожиданная ошибка в handle_stats для группы {stats.get('Internal ID', 'unknown')} (тип {stats_type})")
        raise
