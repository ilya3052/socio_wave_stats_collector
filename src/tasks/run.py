import asyncio

from .create import create_processing_tasks, create_sending_tasks


async def run_processing_tasks(accounts, **kwargs):
    try:
        tasks = await create_processing_tasks(accounts, **kwargs)
        tasks_result = asyncio.gather(*tasks)
        return await tasks_result
    except ValueError:
        raise


async def run_sending_tasks(stats_results, stats_type):
    tasks = await create_sending_tasks(stats_results, stats_type)
    tasks_result = asyncio.gather(*tasks)
    return await tasks_result
