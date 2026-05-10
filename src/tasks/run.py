import asyncio
import logging

from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.exceptions import GroupsNotFoundError, GroupHandleError
from .create import create_processing_tasks, create_sending_tasks

logger = logging.getLogger(__name__)


async def run_processing_tasks(accounts, **options):
    try:
        tasks = await create_processing_tasks(accounts, **options)
        logger.info(f"Запуск {len(tasks)} задач обработки статистики")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failed = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Задача {tasks[i].get_name()} упала с ошибкой: {result}")
                failed += 1

        if failed:
            logger.warning(f"{failed} из {len(tasks)} задач завершились с ошибкой")
        else:
            logger.info(f"Все {len(tasks)} задач успешно завершены")

        return results
    except (ValueError, GroupsNotFoundError, GroupHandleError):
        raise
    except Exception:
        logger.exception("Критическая ошибка при выполнении run_processing_tasks")
        raise


async def run_sending_tasks(stats_results, stats_type):
    try:
        tasks = await create_sending_tasks(stats_results, stats_type)
        if not tasks:
            logger.warning(f"Задачи отправки не созданы - все группы пропущены или упали с ошибками. Подробнее см. в логах")
            return []
        logger.info(f"Запуск {len(tasks)} задач отправки статистики в БД")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failed = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Задача {tasks[i].get_name()} упала с ошибкой: {result}")
                failed += 1

        if failed:
            logger.warning(f"{failed} из {len(tasks)} задач завершились с ошибкой")
        else:
            logger.info(f"Все {len(tasks)} задач успешно завершены")

        return results
    except ValidationError:
        raise
    except ValueError:
        raise
    except NoResultFound:
        raise
    except Exception:
        logger.exception("Критическая ошибка при выполнении run_sending_tasks")
        raise
