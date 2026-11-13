import asyncio
import json

import aio_pika

from app.dependencies import get_redis_cache, get_youtube_circuit_breaker
from app.application.internal.command_services.default_learning_path_recommendation_service import (
    DefaultLearningPathRecommendationService,
)
from app.infrastructure.clients.youtube_data_api_client import YouTubeDataApiClient
from app.infrastructure.configuration.settings import get_settings
from app.observability import configure_logging


EVENT_EXCHANGE = "pathbridge.events"
EVENT_TYPE = "gap_report.generated"
WORK_QUEUE = "learning-pathway.gap-report"
RETRY_EXCHANGE = "pathbridge.retry"
RETRY_QUEUE = "learning-pathway.gap-report.retry"
DEAD_LETTER_EXCHANGE = "pathbridge.dead-letter"
DEAD_LETTER_QUEUE = "learning-pathway.gap-report.dlq"
MAX_RETRIES = 3
MAX_SKILLS_TO_PREWARM = 10


async def _declare_topology(channel: aio_pika.abc.AbstractChannel):
    event_exchange = await channel.declare_exchange(EVENT_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)
    retry_exchange = await channel.declare_exchange(RETRY_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)
    dead_letter_exchange = await channel.declare_exchange(
        DEAD_LETTER_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
    )
    work_queue = await channel.declare_queue(
        WORK_QUEUE,
        durable=True,
        arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE},
    )
    await work_queue.bind(event_exchange, routing_key=EVENT_TYPE)
    retry_queue = await channel.declare_queue(
        RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": 30000,
            "x-dead-letter-exchange": EVENT_EXCHANGE,
            "x-dead-letter-routing-key": EVENT_TYPE,
        },
    )
    await retry_queue.bind(retry_exchange, routing_key=WORK_QUEUE)
    dead_letter_queue = await channel.declare_queue(DEAD_LETTER_QUEUE, durable=True)
    await dead_letter_queue.bind(dead_letter_exchange, routing_key=EVENT_TYPE)
    return work_queue, retry_exchange


async def _prewarm_videos(payload: dict) -> None:
    skills = payload.get("missing_hard_skills")
    if not isinstance(skills, list):
        raise ValueError("Event is missing missing_hard_skills.")
    settings = get_settings()
    client = YouTubeDataApiClient(
        settings.youtube_data_api_key,
        get_redis_cache(),
        get_youtube_circuit_breaker(),
    )
    for skill in skills[:MAX_SKILLS_TO_PREWARM]:
        if not isinstance(skill, str) or not skill.strip():
            continue
        await client.search_videos(
            DefaultLearningPathRecommendationService.video_search_query(skill.strip()),
            max_results=DefaultLearningPathRecommendationService.CANDIDATES_PER_SKILL,
        )


async def _retry_or_dead_letter(
    message: aio_pika.abc.AbstractIncomingMessage,
    retry_exchange: aio_pika.abc.AbstractExchange,
    logger,
) -> None:
    retries = int(message.headers.get("x-retry-count", 0)) if message.headers else 0
    if retries >= MAX_RETRIES:
        await message.reject(requeue=False)
        logger.exception("event_dead_lettered", extra={"event_type": EVENT_TYPE})
        return
    headers = dict(message.headers or {})
    headers["x-retry-count"] = retries + 1
    await retry_exchange.publish(
        aio_pika.Message(
            body=message.body,
            headers=headers,
            content_type=message.content_type,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            message_id=message.message_id,
            correlation_id=message.correlation_id,
            type=message.type,
        ),
        routing_key=WORK_QUEUE,
    )
    await message.ack()
    logger.exception("event_retry_scheduled", extra={"event_type": EVENT_TYPE})


async def run() -> None:
    settings = get_settings()
    logger = configure_logging("learning-pathway-worker")
    if not settings.rabbitmq_url:
        raise RuntimeError("RABBITMQ_URL is required for the learning-pathway worker.")
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    try:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        work_queue, retry_exchange = await _declare_topology(channel)
        logger.info("event_consumer_started", extra={"event_type": EVENT_TYPE})
        async with work_queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    payload = json.loads(message.body)
                    if payload.get("event_type") != EVENT_TYPE:
                        raise ValueError("Unexpected event type.")
                    await _prewarm_videos(payload)
                    await message.ack()
                    logger.info("event_consumed", extra={"event_type": EVENT_TYPE})
                except Exception:
                    await _retry_or_dead_letter(message, retry_exchange, logger)
    finally:
        await get_redis_cache().close()
        await connection.close()


if __name__ == "__main__":
    asyncio.run(run())
