import asyncio

from _asyncio import Task
from pydantic import ValidationError

from src.api import get_api
from src.core import Platforms
from src.exceptions.exceptions import GroupsNotFoundError, GroupHandleError
from src.models import ServiceAccountModel
from src.stats import handle_stats
from src.stats.collect import collect_stats


async def create_processing_tasks(accounts, **kwargs):
    try:
        tasks: list[Task] = []
        for idx, account in enumerate(accounts):  # type: int, ServiceAccountModel
            groups = account.groups
            if not groups:
                raise GroupsNotFoundError('Произошла ошибка при получении групп для сервисного аккаунта')

            platform: Platforms = kwargs.get('platform')
            api = await get_api(account.data, platform)

            if not api:
                raise ValueError('Произошла ошибка при получении объекта API')

            tasks.append(asyncio.create_task(
                collect_stats(groups, api, platform, **{'Type': kwargs.get('Type')}),
                name=f'processing-by-{platform.alias}-acc-№{idx + 1}'))

        return tasks
    except ValueError:
        raise
    except GroupsNotFoundError:
        raise
    except GroupHandleError:
        raise


async def create_sending_tasks(stats_results, stats_type):
    try:
        tasks: list[Task] = []
        for account in stats_results:
            for group_stats in account:
                tasks.append(asyncio.create_task(
                    handle_stats(group_stats, stats_type)
                ))

        return tasks
    except ValidationError:
        raise
