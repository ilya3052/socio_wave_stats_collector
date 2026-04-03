from pydantic import ValidationError

from src.core import Session
from src.models import AbsoluteStatsSchema, SnapshotSchemaCreate, SnapshotModel, SnapshotStatsSchemaCreate, \
    SnapshotStatsModel, AbsoluteStatsSchemaCreate, AbsoluteStatsModel
from src.repositories import AbsoluteStatsRepository, SnapshotRepository, SnapshotStatsRepository


async def send_daily_stats_to_db(stats, snapshot_type):
    for stats_elem in stats:
        try:
            with Session() as session:
                group_id = stats_elem.get('External ID')
                abs_repo = AbsoluteStatsRepository(session)
                abs_stats_instance = abs_repo.get_by_group(group_id)
                abs_stats_schema = AbsoluteStatsSchema.model_validate(abs_stats_instance)
                participants_count = abs_stats_schema.participants_count

                snapshot_repo = SnapshotRepository(session)
                snapshot_schema = SnapshotSchemaCreate.model_validate({
                    "type": snapshot_type,
                    "group_id": stats_elem.get('Internal ID')
                })
                snapshot_instance = SnapshotModel(**snapshot_schema.model_dump())

                snapshot_id = snapshot_repo.add(snapshot_instance)

                snapshot_stats_repo = SnapshotStatsRepository(session)
                snapshot_stats_schema = SnapshotStatsSchemaCreate.model_validate({
                    "repost_count": stats_elem.get('Репосты', 0),
                    "likes_count": stats_elem.get('Лайки', 0),
                    "views_count": stats_elem.get('Просмотры', 0),
                    "participants_delta": participants_count - stats_elem.get('Подписчики', 0),
                    "comms_count": stats_elem.get('Комментарии', 0),
                    "snapshot_id": snapshot_id,
                    "coverage": 1
                })
                snapshot_stats_repo.add(SnapshotStatsModel(**snapshot_stats_schema.model_dump()))

                snapshot_repo.commit()
                snapshot_stats_repo.commit()
        except ValidationError as VE:
            print(VE)
            return False
    return True


async def send_absolute_stats_to_db(stats):
    for stats_elem in stats:
        try:
            with Session() as session:
                absolute_stats_repo = AbsoluteStatsRepository(session)
                absolute_stats_schema = AbsoluteStatsSchemaCreate.model_validate({
                    "likes_count": stats_elem.get('Лайки'),
                    "views_count": stats_elem.get('Просмотры'),
                    "participants_count": stats_elem.get('Подписчики'),
                    "repost_count": stats_elem.get('Репосты'),
                    "comms_count": stats_elem.get('Комментарии'),
                    "group_id": stats_elem.get('Internal ID')
                })
                absolute_stats_instance = AbsoluteStatsModel(**absolute_stats_schema.model_dump())
                absolute_stats_repo.add(absolute_stats_instance)
                absolute_stats_repo.commit()
        except ValidationError as VE:
            print(VE)
            return False
    return True
