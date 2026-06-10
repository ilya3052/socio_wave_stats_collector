import logging
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.core import Session
from src.models import AbsoluteStatsSchema, SnapshotSchemaCreate, SnapshotModel, SnapshotStatsSchemaCreate, \
    SnapshotStatsModel, AbsoluteStatsModel, BestPostInfoSchemaCreate, BestPostInfoModel, GroupModel, \
    PostMetricsSchemaCreate, PostMetricsModel
from src.repositories import AbsoluteStatsRepository, SnapshotRepository, SnapshotStatsRepository, \
    BestPostsInfoRepository, GroupsRepository, PostMetricsRepository
from src.tools import get_aggregated_post_data
from src.tools.interval_distribution import update_intervals

logger = logging.getLogger(__name__)


async def send_stats_to_db(stats, snapshot_type):
    try:
        with Session() as session:
            group_id = stats.get('Internal ID')

            group_repo = GroupsRepository(session)
            group_instance = group_repo.get(group_id)
            aggregated_post_data = group_instance.aggregated_post_data

            logger.debug(f"Сохранение {snapshot_type.value} статистики для группы с ID {group_id}")

            abs_repo = AbsoluteStatsRepository(session)
            abs_stats_instance: AbsoluteStatsModel = abs_repo.get_by_group(group_id)
            abs_stats_schema = AbsoluteStatsSchema.model_validate(abs_stats_instance)
            participants_count = abs_stats_schema.participants_count

            snapshot_repo = SnapshotRepository(session)
            snapshot_schema = SnapshotSchemaCreate.model_validate({
                "type": snapshot_type,
                "group_id": group_id
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
            err = 0
            if views_count > 0:
                err = round(((likes_count + repost_count + comms_count) / views_count), 4)
            snapshot_stats_schema = SnapshotStatsSchemaCreate.model_validate({
                "repost_count": repost_count,
                "likes_count": likes_count,
                "views_count": views_count,
                "participants_delta": participants_delta,
                "comms_count": comms_count,
                "snapshot_id": snapshot_id,
                "ERR": err
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

            if 'additional_data' not in stats:
                session.commit()
                logger.info(f"{snapshot_type.value} статистика успешно сохранена в БД для группы с ID {group_id}")
                return True

            metrics_repo = PostMetricsRepository(session)
            additional_data = stats.get('additional_data')
            post_data = update_intervals(additional_data, aggregated_post_data)
            group_instance.aggregated_post_data = post_data

            for data in additional_data:
                post = additional_data[data]
                likes_count = post.get('likes_count', 0)
                comms_count = post.get('comms_count', 0)
                repost_count = post.get('repost_count', 0)

                metrics_schema = PostMetricsSchemaCreate.model_validate({
                    'post_id': data,
                    'likes_count': likes_count,
                    'comms_count': comms_count,
                    'reposts_count': repost_count,
                    'views_count': post.get('views_count'),
                    'hour': post.get('hour'),
                    'day_of_week': post.get('day_of_week'),
                    'is_weekend': post.get('is_weekend'),
                    'text_length': post.get('text_length'),
                    'group_id': group_id,
                    "timestamp": datetime.now(),

                    "like_view_ratio": post.get("like_view_ratio"),
                    "has_video": post.get("has_video"),
                    "has_photo": post.get("has_photo"),
                    "word_count": post.get('word_count')
                })
                metrics_instance = PostMetricsModel(**metrics_schema.model_dump())
                metrics_repo.add(metrics_instance)
            session.commit()

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
    service_data = stats.get('service_data')
    posts_stats = service_data.get('posts_stats')
    max_likes = service_data.get('max_likes')
    max_reposts = service_data.get('max_reposts')
    max_comments = service_data.get('max_comments')

    aggregated_data = get_aggregated_post_data(posts_stats, max_likes, max_reposts, max_comments)

    try:
        with Session() as session:
            group_id = stats.get('Internal ID')
            logger.debug(f"Сохранение абсолютной статистики для группы с ID {group_id}")

            group_repo = GroupsRepository(session)
            group = group_repo.get(group_id)
            group.status = 'SUCCESS'
            group.aggregated_post_data = aggregated_data

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
            session.commit()

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
                session.commit()
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
            session.commit()

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
