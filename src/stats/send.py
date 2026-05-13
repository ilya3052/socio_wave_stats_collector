import logging
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.core import Session
from src.models import AbsoluteStatsSchema, SnapshotSchemaCreate, SnapshotModel, SnapshotStatsSchemaCreate, \
    SnapshotStatsModel, AbsoluteStatsModel, BestPostInfoSchemaCreate, BestPostInfoModel, GroupModel
from src.repositories import AbsoluteStatsRepository, SnapshotRepository, SnapshotStatsRepository, \
    BestPostsInfoRepository, GroupsRepository

logger = logging.getLogger(__name__)


async def send_stats_to_db(stats, snapshot_type):
    try:
        with Session() as session:
            group_id = stats.get('Internal ID')

            logger.debug(f"Сохранение {snapshot_type.value} статистики для группы с ID {group_id}")

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
            participants_delta = stats.get('Подписчики', 0) - participants_count
            comms_count = stats.get('Комментарии', 0)
            posts_count = stats.get('Количество записей', 0)

            snapshot_stats_schema = SnapshotStatsSchemaCreate.model_validate({
                "repost_count": repost_count,
                "likes_count": likes_count,
                "views_count": views_count,
                "participants_delta": participants_delta,
                "comms_count": comms_count,
                "snapshot_id": snapshot_id,
                # "coverage": round(((likes_count + repost_count + comms_count) / views_count) * 100, 2) # заменить название поля на ERR
                "coverage": 1  # заменить название поля на ERR
            })
            snapshot_stats_repo.add(SnapshotStatsModel(**snapshot_stats_schema.model_dump()))
            abs_repo.update(abs_stats_instance.id, {
                "repost_count": abs_stats_instance.repost_count + repost_count,
                "likes_count": abs_stats_instance.likes_count + likes_count,
                "views_count": abs_stats_instance.views_count + views_count,
                "participants_count": abs_stats_instance.participants_count + participants_delta,
                "comms_count": abs_stats_instance.comms_count + comms_count,
                "posts_count": abs_stats_instance.posts_count + posts_count,
                "last_updated_at": datetime.now()
            })
            abs_repo.commit()
            snapshot_repo.commit()
            snapshot_stats_repo.commit()
        logger.info(f"{snapshot_type.value} статистика успешно сохранена в БД для группы с ID {group_id}")
        return True
    except ValidationError as e:
        logger.error(
            f"Ошибка валидации при сохранении статистики для группы {stats.get('Internal ID', 'unknown')}: {e}")
        raise
    except NoResultFound as e:
        logger.error(
            f"Ошибка NoResultFound при сохранении статистики для группы {stats.get('Internal ID', 'unknown')}: {e}")
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка в send_daily_stats_to_db для группы {stats.get('Internal ID', 'unknown')}")
        raise


async def send_absolute_stats_to_db(stats):
    try:
        with Session() as session:
            group_id = stats.get('Internal ID')
            logger.debug(f"Сохранение абсолютной статистики для группы с ID {group_id}")

            absolute_stats_repo = AbsoluteStatsRepository(session)
            absolute_stats_instance = absolute_stats_repo.get_by_group(group_id)
            absolute_stats_repo.update(absolute_stats_instance.id, {
                "likes_count": stats.get('Лайки'),
                "views_count": stats.get('Просмотры'),
                "participants_count": stats.get('Подписчики'),
                "repost_count": stats.get('Репосты'),
                "comms_count": stats.get('Комментарии'),
                "posts_count": stats.get('Количество записей'),
                "last_updated_at": datetime.now(),
                "group_id": group_id
            })
            absolute_stats_repo.commit()

        logger.info(f"Абсолютная статистика успешно сохранена в БД для группы с ID {stats.get('Internal ID')}")
        return True
    except ValidationError as e:
        logger.error(
            f"Ошибка валидации при сохранении абсолютной статистики для группы {stats.get('Internal ID', 'unknown')}: {e}")
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка в send_absolute_stats_to_db для группы {stats.get('Internal ID', 'unknown')}")
        raise


async def send_top_posts_stats_to_db(stats):
    try:
        with Session() as session:
            group_id = stats.get('External ID')
            top_posts = stats.get('top_posts')

            groups_repo = GroupsRepository(session)
            group: GroupModel = groups_repo.get_by_external_id(group_id)
            internal_id = group.id

            best_posts_repo = BestPostsInfoRepository(session)
            best_posts = best_posts_repo.get_by_group_id(internal_id)

            if best_posts:
                for item, instance in zip(top_posts, best_posts):  # type: str, BestPostInfoModel
                    processed_item = top_posts[item]
                    best_posts_repo.update(instance.id, {
                        "likes_count": processed_item.get('likes_count'),
                        "comms_count": processed_item.get('comms_count'),
                        "views_count": processed_item.get('views_count'),
                        "reposts_count": processed_item.get('reposts_count'),
                        "content": processed_item.get('content'),
                        "post_id": processed_item.get('id'),
                        "post_type": item.upper(),
                        "group_id": internal_id,
                        "last_updated_at": datetime.now()
                    })
                best_posts_repo.commit()
                return True

            for item in top_posts:
                processed_item = top_posts[item]
                best_posts_schema = BestPostInfoSchemaCreate.model_validate({
                    "likes_count": processed_item.get('likes_count'),
                    "comms_count": processed_item.get('comms_count'),
                    "views_count": processed_item.get('views_count'),
                    "reposts_count": processed_item.get('reposts_count'),
                    "content": processed_item.get('content'),
                    "post_id": processed_item.get('id'),
                    "post_type": item,
                    "group_id": internal_id
                })
                best_posts_instance = BestPostInfoModel(**best_posts_schema.model_dump())
                best_posts_repo.add(best_posts_instance)
            best_posts_repo.commit()

        logger.info(f"Обновленный недельный топ постов в БД для группы с ID {stats.get('Internal ID')} сохранен")
        return True
    except ValidationError as e:
        logger.error(
            f"Ошибка валидации при сохранении недельного топа постов для группы {stats.get('Internal ID', 'unknown')}: {e}")
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка в send_top_posts_stats_to_db для группы {stats.get('Internal ID', 'unknown')}")
        raise
