from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.core import SnapshotType


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
        alias="group_addedAt",
        le=date.today(),
        default=date.today()
    )

    serviceAccount_id: int = Field(description="Внешний ключ для связи с сервисным аккаунтом")
    platform_id: int = Field(description="Внешний ключ для связи с записью платформы")


class AbsoluteStatsSchemaBase(ParentSchemaConfig):
    likes_count: int = Field(
        alias="absoluteStats_likesCount",
        description="Общее количество лайков",
        ge=0
    )
    views_count: int = Field(
        alias="absoluteStats_viewsCount",
        description="Общее количество просмотров",
        ge=0
    )
    participants_count: int = Field(
        alias="absoluteStats_participantsCount",
        description="Общее количество просмотров",
        ge=0
    )
    repost_count: int = Field(
        alias="absoluteStats_repostCount",
        description="Общее количество репостов",
        ge=0
    )
    comms_count: int = Field(
        alias="absoluteStats_commsCount",
        description="Общее количество комментариев",
        ge=0
    )

    last_updated_at: datetime = Field(
        alias="absoluteStats_lastUpdatedAt",
        description="Время последнего обновления",
        le=datetime.now(),
        default=datetime.now()
    )

    group_id: int = Field(description="Внешний ключ для связи с группой")


class AbsoluteStatsSchema(AbsoluteStatsSchemaBase):
    id: int = Field(
        alias="absoluteStats_id",
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
        alias="snapshotStats_repostCount",
        description="Количество репостов в разнице с абсолютной статистиков",
        ge=0
    )
    likes_count: int = Field(
        alias="snapshotStats_likesCount",
        description="Количество лайков в разнице с абсолютной статистикой",
        ge=0
    )
    views_count: int = Field(
        alias="snapshotStats_viewsCount",
        description="Количество просмотров в разнице с абсолютной статистикой",
        ge=0
    )
    participants_delta: int = Field(
        alias="snapshotStats_participantsCount",
        description="Количество просмотров в разнице с абсолютной статистикой",
    )
    coverage: int = Field(
        alias="snapshotStats_coverage",
        description="Охваты"
    )
    comms_count: int = Field(
        alias="snapshotStats_commsCount",
        description="Общее количество комментариев",
        ge=0
    )

    snapshot_id: int = Field(description="Внешний ключ для связи с записью снапшота")


class SnapshotStatsSchema(SnapshotStatsSchemaBase):
    id: int = Field(
        alias="snapshotStats_id",
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
        alias="serviceAccount_id",
        description="Уникальный ID сервисного аккаунта"
    )
    name: str = Field(
        alias="serviceAccount_name",
        max_length=128,
        description="Имя сервисного аккаунта на платформе"
    )

    platform_id: int = Field(description="Внешний ключ для связи с платформой")

    app_id: Optional[int] = Field(
        alias="serviceAccount_app_id",
        description="appID приложения ВК",
        default=None
    )

    is_activated: bool = Field(
        alias="serviceAccount_is_activated",
        description="Статус активации аккаунта"
    )


class ServiceAccountDataSchema(ParentSchemaConfig):
    id: int = Field(
        alias="serviceAccountData_id",
        description="Уникальный ID записи о данных сервисного аккаунта"
    )
    service_key: Optional[str] = Field(
        alias="serviceAccountData_serviceKey",
        max_length=256,
        description="Сервисный ключ приложения ВК",
        default=None
    )
    protected_key: Optional[str] = Field(
        alias="serviceAccountData_protectedKey",
        max_length=256,
        description="Защищенный ключ приложения ВК",
        default=None
    )
    phone_number: Optional[str] = Field(
        alias="serviceAccountData_phoneNumber",
        min_length=11,
        max_length=11,
        description="Номер телефона аккаунта ТГ",
        default=None
    )
    session_path: Optional[str] = Field(
        alias="serviceAccountData_sessionPath",
        max_length=256,
        description='Путь к файлу сессии аккаунта ТГ',
        default=None
    )

    serviceAccount_id: int = Field(description="Внешний ключ для связи с данными сервисного аккаунта")
