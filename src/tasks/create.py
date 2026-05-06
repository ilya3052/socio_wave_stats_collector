import asyncio
import logging

from _asyncio import Task

from src.api import get_api
from src.core import Platforms
from src.exceptions import GroupsNotFoundError, GroupHandleError
from src.models import ServiceAccountModel
from src.stats import handle_stats, collect_stats

logger = logging.getLogger(__name__)


async def create_processing_tasks(accounts, **options):
    try:
        tasks: list[Task] = []
        platform = options.pop('platform')
        stats_type = options.get('Type')

        logger.info(
            f"Создание задач обработки для {len(accounts)} аккаунтов на платформе {platform.alias.upper()} (тип снапшота - {stats_type.value})")

        for idx, account in enumerate(accounts, 1):  # type: int, ServiceAccountModel
            groups = account.groups
            if not groups:
                logger.error(
                    f"GroupsNotFoundError для сервисного аккаунта с ID {account.id} (платформа {platform.alias})")
                raise GroupsNotFoundError('Произошла ошибка при получении групп для сервисного аккаунта')

            api = await get_api(account.data, platform)

            if not api:
                logger.error(f"Не удалось получить API для аккаунта с ID {account.id} (платформа {platform.alias})")
                raise ValueError('Произошла ошибка при получении объекта API')
            tasks.append(asyncio.create_task(
                collect_stats(groups, api, platform, **options),
                name=f'processing-by-{platform.alias}-acc-№{idx}'))

        logger.info(f"Создано {len(tasks)} задач обработки для платформы {platform.alias.upper()}")
        return tasks

    except (ValueError, GroupsNotFoundError, GroupHandleError):
        raise
    except Exception as e:
        logger.exception("Неожиданная ошибка при создании задач обработки")
        raise


async def create_sending_tasks(stats_results, stats_type):
    try:
        tasks: list[Task] = []
        logger.info(f"Создание задач отправки статистики (тип: {stats_type.value}, групп: {len(stats_results)})")

        for account_stats in stats_results:
            for group_stats in account_stats:
                tasks.append(asyncio.create_task(
                    handle_stats(group_stats, stats_type),
                    name=f'sending-stats-group-{group_stats.get("Internal ID", "unknown")}'
                ))

        logger.info(f"Создано {len(tasks)} задач отправки в БД")
        return tasks

    except Exception:
        logger.exception("Ошибка при создании задач отправки")
        raise
