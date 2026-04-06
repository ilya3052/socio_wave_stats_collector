import asyncio

from pydantic import ValidationError

from .create import create_processing_tasks, create_sending_tasks
from ..exceptions.exceptions import GroupsNotFoundError, GroupHandleError


async def run_processing_tasks(accounts, **kwargs):
    try:
        tasks = await create_processing_tasks(accounts, **kwargs)
        tasks_result = asyncio.gather(*tasks)
        return await tasks_result
    except ValueError:
        raise
    except GroupsNotFoundError:
        raise
    except GroupHandleError:
        raise


async def run_sending_tasks(stats_results, stats_type):
    try:
        tasks = await create_sending_tasks(stats_results, stats_type)
        tasks_result = asyncio.gather(*tasks)
        return await tasks_result
    except ValidationError:
        raise
    except ValueError:
        raise
