from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.core import SnapshotType, BestPostInfoType


class ParentSchemaConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid', populate_by_name=True)


class GroupSchema(ParentSchemaConfig):
    id: int = Field(
        alias="group_id",
        description="Уникальный ID группы в системе"
    )
    external_id: int = Field(
        alias='group_externalID',
        description='ID группы на платформе'
    )
    name: str = Field(
        alias="group_name",
        max_length=128,
        description="Название группы"
    )
    link: str = Field(
        alias="group_link",
        max_length=256,
        description="Полная ссылка на группу"
    )
    added_at: date = Field(
        alias="group_added_at",
        le=date.today(),
        default=date.today()
    )

    post_data: dict = Field(alias="predictive_models_params", description="Параметры модели в формате JSON")

    service_account_id: int = Field(description="Внешний ключ для связи с сервисным аккаунтом")
    platform_id: int = Field(description="Внешний ключ для связи с записью платформы")


class BestPostInfoSchemaBase(ParentSchemaConfig):
    likes_count: int = Field(
        alias="bestpostinfo_likes_count",
        description="Количество лайков записи"
    )
    comms_count: int = Field(
        alias="bestpostinfo_comms_count",
        description="Количество комментариев записи"
    )
    views_count: int = Field(
        alias="bestpostinfo_views_count",
        description="Количество просмотров записи"
    )
    reposts_count: int = Field(
        alias="bestpostinfo_reposts_count",
        description="Количество репостов записи"
    )
    content: str = Field(
        alias="bestpostinfo_content",
        description="Текст записи",
        max_length=150
    )
    post_id: int = Field(
        alias="bestpostinfo_post_id",
        description="ID записи в группе"
    )
    post_type: BestPostInfoType = Field(
        alias="bestpostinfo_type",
        description="Признак поста"
    )

    last_updated_at: datetime = Field(
        alias="bestpostinfo_last_updated_at",
        description="Время последнего обновления",
        le=datetime.now(),
        default=datetime.now()
    )

    group_id: int = Field(description="Внешний ключ для связи с записью группы")


class BestPostInfoSchema(BestPostInfoSchemaBase):
    id: int = Field(
        alias="bestpostinfo_id",
        description="Уникальный ID записи"
    )


class BestPostInfoSchemaCreate(BestPostInfoSchemaBase):
    pass


class AbsoluteStatsSchemaBase(ParentSchemaConfig):
    likes_count: int = Field(
        alias="absolute_stats_likes_count",
        description="Общее количество лайков",
        ge=0,
        default=0
    )
    views_count: int = Field(
        alias="absolute_stats_views_count",
        description="Общее количество просмотров",
        ge=0,
        default=0
    )
    participants_count: int = Field(
        alias="absolute_stats_participants_count",
        description="Общее количество просмотров",
        ge=0,
        default=0
    )
    repost_count: int = Field(
        alias="absolute_stats_repost_count",
        description="Общее количество репостов",
        ge=0,
        default=0
    )
    comms_count: int = Field(
        alias="absolute_stats_comms_count",
        description="Общее количество комментариев",
        ge=0,
        default=0
    )

    last_updated_at: datetime = Field(
        alias="absolute_stats_last_updated_at",
        description="Время последнего обновления",
        le=datetime.now(),
        default=datetime.now()
    )

    posts_count: int = Field(
        alias="absolute_stats_posts_count",
        description='Общее количество записей в группе',
        ge=0,
        default=0
    )

    group_id: int = Field(description="Внешний ключ для связи с группой")


class AbsoluteStatsSchema(AbsoluteStatsSchemaBase):
    id: int = Field(
        alias="absolute_stats_id",
        description="Уникальный ID записи"
    )


class AbsoluteStatsSchemaCreate(AbsoluteStatsSchemaBase):
    pass


class SnapshotSchemaBase(ParentSchemaConfig):
    timestamp: datetime = Field(
        alias="snapshot_timestamp",
        le=datetime.now(),
        default=datetime.now(),
        description="Время снимка состояния"
    )
    type: SnapshotType = Field(
        alias="snapshot_type",
        description="Тип снимка состояния"
    )

    group_id: int = Field(description="Внешний ключ для связи с группой")


class SnapshotSchema(SnapshotSchemaBase):
    id: Optional[int] = Field(
        alias="snapshot_id",
        description="Уникальный ID записи"
    )


class SnapshotSchemaCreate(SnapshotSchemaBase):
    pass


class SnapshotStatsSchemaBase(ParentSchemaConfig):
    repost_count: int = Field(
        alias="snapshot_stats_repost_count",
        description="Количество репостов в разнице с абсолютной статистиков",
        ge=0
    )
    likes_count: int = Field(
        alias="snapshot_stats_likes_count",
        description="Количество лайков в разнице с абсолютной статистикой",
        ge=0
    )
    views_count: int = Field(
        alias="snapshot_stats_views_count",
        description="Количество просмотров в разнице с абсолютной статистикой",
        ge=0
    )
    participants_delta: int = Field(
        alias="snapshot_stats_participants_count",
        description="Количество просмотров в разнице с абсолютной статистикой",
    )
    ERR: Decimal = Field(
        alias="snapshot_stats_err",
        description="ERR"
    )
    comms_count: int = Field(
        alias="snapshot_stats_comms_count",
        description="Общее количество комментариев",
        ge=0
    )

    snapshot_id: int = Field(description="Внешний ключ для связи с записью снапшота")


class SnapshotStatsSchema(SnapshotStatsSchemaBase):
    id: int = Field(
        alias="snapshot_stats_id",
        description="Уникальный ID снапшота"
    )


class SnapshotStatsSchemaCreate(SnapshotStatsSchemaBase):
    pass


class PlatformSchema(ParentSchemaConfig):
    id: int = Field(
        alias="platform_id",
        description="Уникальный ID платформы"
    )
    name: str = Field(
        alias="platform_name",
        max_length=128,
        description="Название платформы"
    )

    alias: str = Field(
        alias="platform_alias",
        max_length=16,
        description="Алиас платформы"
    )


class ServiceAccountSchema(ParentSchemaConfig):
    id: int = Field(
        alias="service_account_id",
        description="Уникальный ID сервисного аккаунта"
    )
    name: str = Field(
        alias="service_account_name",
        max_length=128,
        description="Имя сервисного аккаунта на платформе"
    )

    platform_id: int = Field(description="Внешний ключ для связи с платформой")

    app_id: Optional[int] = Field(
        alias="service_account_app_id",
        description="appID приложения ВК",
        default=None
    )

    is_activated: bool = Field(
        alias="service_account_is_activated",
        description="Статус активации аккаунта"
    )


class ServiceAccountDataSchema(ParentSchemaConfig):
    id: int = Field(
        alias="service_accountData_id",
        description="Уникальный ID записи о данных сервисного аккаунта"
    )
    service_key: Optional[str] = Field(
        alias="service_accountData_service_key",
        max_length=256,
        description="Сервисный ключ приложения ВК",
        default=None
    )
    protected_key: Optional[str] = Field(
        alias="service_accountData_protected_key",
        max_length=256,
        description="Защищенный ключ приложения ВК",
        default=None
    )
    phone_number: Optional[str] = Field(
        alias="service_accountData_phone_number",
        min_length=11,
        max_length=11,
        description="Номер телефона аккаунта ТГ",
        default=None
    )
    session_path: Optional[str] = Field(
        alias="service_accountData_session_path",
        max_length=256,
        description='Путь к файлу сессии аккаунта ТГ',
        default=None
    )

    service_account_id: int = Field(description="Внешний ключ для связи с данными сервисного аккаунта")


class PostMetricsSchemaBase(ParentSchemaConfig):
    post_id: int = Field(
        alias="stats_postmetrics_post_id",
        description="ID поста в группе для которого собираются метрики"
    )
    likes_count: int = Field(
        alias="stats_postmetrics_likes_count",
        description="Количество лайков поста"
    )
    views_count: int = Field(
        alias="stats_postmetrics_views_count",
        description="Количество просмотров поста"
    )
    reposts_count: int = Field(
        alias="stats_postmetrics_repost_count",
        description="Количество репостов поста"
    )
    comms_count: int = Field(
        alias="stats_postmetrics_comms_count",
        description="Количество комментариев поста"
    )
    hour: int = Field(
        alias="stats_postmetrics_hour",
        description="Час публикации"
    )
    day_of_week: int = Field(
        alias="stats_postmetrics_day_of_week",
        description="День публикации"
    )
    is_weekend: bool = Field(
        alias="stats_postmetrics_is_weekend",
        description="Признак публикации в выходной день"
    )

    text_length: int = Field(
        alias="stats_postmetrics_text_length",
        description="Длина текста поста"
    )

    like_view_ratio: float = Field(
        alias="stats_postmetrics_like_view_ratio",
        description="Соотношение лайков к просмотрам"
    )
    has_video: bool = Field(
        alias="stats_postmetrics_has_video",
        description="Признак наличия видео в посте"
    )
    has_photo: bool = Field(
        alias="stats_postmetrics_has_photo",
        description="Признак наличия фото в посте"
    )
    word_count: int = Field(
        alias="stats_postmetrics_word_count",
        description="Количество слов в посте"
    )

    group_id: int = Field(description="Внешний ключ для связи с группой")
    timestamp: datetime = Field(alias="stats_postmetrics_timestamp", default=datetime.now())


class PostMetricsSchema(PostMetricsSchemaBase):
    id: int = Field(alias="", description="")


class PostMetricsSchemaCreate(PostMetricsSchemaBase):
    pass
