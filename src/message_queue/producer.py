import logging

from aio_pika import Message

from src.core.config import get_channel

logger = logging.getLogger(__name__)


async def publish_task(message: str, queue_name: str = "abs-stats"):
    channel = await get_channel()
    await channel.declare_queue(queue_name, durable=True)
    await channel.default_exchange.publish(
        Message(body=message.encode()),
        routing_key=queue_name,
    )
    logger.info("В очередь '%s' было успешно отправлено сообщение", queue_name)
