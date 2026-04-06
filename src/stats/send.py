from datetime import datetime

from pydantic import ValidationError

from src.core import Session
from src.models import AbsoluteStatsSchema, SnapshotSchemaCreate, SnapshotModel, SnapshotStatsSchemaCreate, \
    SnapshotStatsModel, AbsoluteStatsSchemaCreate, AbsoluteStatsModel
from src.repositories import AbsoluteStatsRepository, SnapshotRepository, SnapshotStatsRepository


async def send_daily_stats_to_db(stats, snapshot_type):
    try:
        with Session() as session:
            group_id = stats.get('Internal ID')
            abs_repo = AbsoluteStatsRepository(session)
            abs_stats_instance: AbsoluteStatsModel = abs_repo.get_by_group(group_id)
            abs_stats_schema = AbsoluteStatsSchema.model_validate(abs_stats_instance)
            participants_count = abs_stats_schema.participants_count

            snapshot_repo = SnapshotRepository(session)
            snapshot_schema = SnapshotSchemaCreate.model_validate({
                "type": snapshot_type,
                "group_id": stats.get('Internal ID')
            })
            snapshot_instance = SnapshotModel(**snapshot_schema.model_dump())

            snapshot_id = snapshot_repo.add(snapshot_instance)

            snapshot_stats_repo = SnapshotStatsRepository(session)

            repost_count = stats.get('Репосты', 0)
            likes_count = stats.get('Лайки', 0)
            views_count = stats.get('Просмотры', 0)
            participants_delta = participants_count - stats.get('Подписчики', 0)
            comms_count = stats.get('Комментарии', 0)

            snapshot_stats_schema = SnapshotStatsSchemaCreate.model_validate({
                "repost_count": repost_count,
                "likes_count": likes_count,
                "views_count": views_count,
                "participants_delta": participants_delta,
                "comms_count": comms_count,
                "snapshot_id": snapshot_id,
                "coverage": 1
            })
            snapshot_stats_repo.add(SnapshotStatsModel(**snapshot_stats_schema.model_dump()))

            abs_repo.update(abs_stats_instance.id, {
                "repost_count": abs_stats_instance.repost_count + repost_count,
                "likes_count": abs_stats_instance.likes_count + likes_count,
                "views_count": abs_stats_instance.views_count + views_count,
                "participants_count": abs_stats_instance.participants_count + participants_delta,
                "comms_count": abs_stats_instance.comms_count + comms_count,
                "last_updated_at": datetime.now()
            })
            abs_repo.commit()
            snapshot_repo.commit()
            snapshot_stats_repo.commit()
    except ValidationError:
        raise
    return True


async def send_absolute_stats_to_db(stats):
    try:
        with Session() as session:
            absolute_stats_repo = AbsoluteStatsRepository(session)
            absolute_stats_schema = AbsoluteStatsSchemaCreate.model_validate({
                "likes_count": stats.get('Лайки'),
                "views_count": stats.get('Просмотры'),
                "participants_count": stats.get('Подписчики'),
                "repost_count": stats.get('Репосты'),
                "comms_count": stats.get('Комментарии'),
                "group_id": stats.get('Internal ID')
            })
            absolute_stats_instance = AbsoluteStatsModel(**absolute_stats_schema.model_dump())
            absolute_stats_repo.add(absolute_stats_instance)
            absolute_stats_repo.commit()
    except ValidationError:
        raise
    return True
