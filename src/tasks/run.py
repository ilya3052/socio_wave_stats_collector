import asyncio

from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.exceptions import GroupsNotFoundError, GroupHandleError
from .create import create_processing_tasks, create_sending_tasks

import logging
logger = logging.getLogger(__name__)

async def run_processing_tasks(accounts, **kwargs):
    try:
        tasks = await create_processing_tasks(accounts, **kwargs)
        logger.info(f"Запуск {len(tasks)} задач обработки статистики")
        return await asyncio.gather(*tasks, return_exceptions=False)
    except (ValueError, GroupsNotFoundError, GroupHandleError):
        raise
    except Exception:
        logger.exception("Критическая ошибка при выполнении run_processing_tasks")
        raise


async def run_sending_tasks(stats_results, stats_type):
    try:
        tasks = await create_sending_tasks(stats_results, stats_type)
        logger.info(f"Запуск {len(tasks)} задач отправки статистики в БД")
        return await asyncio.gather(*tasks, return_exceptions=False)
    except ValidationError:
        raise
    except ValueError:
        raise
    except NoResultFound:
        raise
    except Exception:
        logger.exception("Критическая ошибка при выполнении run_sending_tasks")
        raise
