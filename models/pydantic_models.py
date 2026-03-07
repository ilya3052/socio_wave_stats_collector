from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class ParentSchemaConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')


class GroupSchema(ParentSchemaConfig):
    id: int = Field(
        alias="group_id",
        description="Уникальный id группы"
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


class AbsoluteStatsSchema(ParentSchemaConfig):
    id: int = Field(
        alias="absoluteStats_id",
        description="Уникальный ID записи"
    )
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
    # необходимо ли?
    coverage: int = Field(
        alias="absoluteStats_coverage",
        description="Охваты"
    )
    last_updated_at: datetime = Field(
        alias="absoluteStats_lastUpdatedAt",
        description="Время последнего обновления",
        le=datetime.now(),
        default=datetime.now()
    )


class SnapshotSchema(ParentSchemaConfig):
    id: int = Field(
        alias="snapshot_id",
        description="Уникальный ID записи"
    )
    # добавить валидацию на проверку корректности id(зависит от того какие приходят от апи)
    last_message_id: int = Field(
        alias="snapshot_lastMessageId",
        description="Последнее обработанное сообщение"
    )
    timestamp: datetime = Field(
        alias="snapshot_timestamp",
        le=datetime.now(),
        default=datetime.now(),
        description="Время снимка состояния"
    )
    type: Literal[0, 1] = Field(
        alias="snapshot_type",
        description="Тип снимка состояния"
    )


class SnapshotStatsSchema(ParentSchemaConfig):
    id: int = Field(
        alias="snapshotStats_id",
        description="Уникальный ID снапшота"
    )
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
    participants_count: int = Field(
        alias="snapshotStats_participantsCount",
        description="Количество просмотров в разнице с абсолютной статистикой",
        ge=0
    )
    coverage: int = Field(
        alias="snapshotStats_coverage",
        description="Охваты"
    )


class ReportSchema(ParentSchemaConfig):
    id: int = Field(
        alias="reportSchema_id",
        description="Уникальный ID записи об отчете"
    )
    filename: str = Field(
        alias="reportSchema_filename",
        max_length=256,
        description="Имя файла"
    )
    path: str = Field(
        alias="reportSchema_path",
        max_length=512,
        description="Полный путь к файла"
    )
    compilation_date: date = Field(
        alias="reportSchema_compilationDate",
        le=date.today(),
        default=date.today(),
        description="Дата создания отчета"
    )
    filetype: Literal['xlsx', 'pdf'] = Field(
        alias="reportSchema_filetype",
        description="Тип отчета"
    )

    """
    подумать над тем возможно ли разовое создание нескольких типов отчетов - если да, сделать аннотацию списком и валидацию
    """

    # @field_validator('filetype', mode='before')
    # @staticmethod
    # def validate_filetype(cls, value):
    #     if isinstance(value, str):
    #         return [value]
    #     return value


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


class ServiceAccount(ParentSchemaConfig):
    id: int = Field(
        alias="serviceAccount_id",
        description="Уникальный ID сервисного аккаунта"
    )
    link: str = Field(
        alias="serviceAccount_link",
        max_length=256,
        description="Ссылка на сервисный аккаунт на платформе"
    )
    name: str = Field(
        alias="serviceAccount_name",
        max_length=128,
        description="Имя сервисного аккаунта на платформе"
    )


class ServiceAccountDataSchema(ParentSchemaConfig):
    id: int = Field(
        alias="serviceAccountData_id",
        description="Уникальный ID записи о данных сервисного аккаунта"
    )
    serviceKey: Optional[str] = Field(
        alias="serviceAccountData_serviceKey",
        max_length=256,
        description="Сервисный ключ приложения ВК"
    )
    protectedKey: Optional[str] = Field(
        alias="serviceAccountData_protectedKey",
        max_length=256,
        description="Защищенный ключ приложения ВК"
    )
    phoneNumber: Optional[str] = Field(
        alias="serviceAccountData_phoneNumber",
        min_length=16,
        max_length=16,
        description="Номер телефона аккаунта ТГ",
        pattern=r"^\+7\(\d{3}\)\s\d{3}-\d{2}-\d{2}$"
    )
