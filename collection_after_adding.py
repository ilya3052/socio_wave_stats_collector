import asyncio
import logging

from src.core import close_rabbitmq
from src.message_queue.consumer import start_consumer

logger = logging.getLogger(__name__)


async def collect_after_adding():
    try:
        await start_consumer()
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Остановка консьюмера...")
    finally:
        await close_rabbitmq()


if __name__ == '__main__':
    asyncio.run(collect_after_adding())
