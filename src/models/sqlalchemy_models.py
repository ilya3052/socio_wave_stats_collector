from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated, Optional

from sqlalchemy import String, text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

today = Annotated[datetime, mapped_column(server_default=text("CURRENT_DATE"))]

str_16 = Annotated[str, 16]
str_128 = Annotated[str, 128]
str_256 = Annotated[str, 256]
str_512 = Annotated[str, 512]


class SnapshotType(IntEnum):
    HOURLY = 0
    DAILY = 1


class FileType(StrEnum):
    XLSX = "xlsx"
    PDF = "pdf"


class Base(DeclarativeBase):
    id: Mapped[int_pk]
    type_annotation_map = {
        str_16: String(16),
        str_128: String(128),
        str_256: String(256),
        str_512: String(512)
    }


class GroupModel(Base):
    __tablename__ = "groups"

    name: Mapped[str_128]
    link: Mapped[str_256]
    added_at: Mapped[created_at]
    serviceAccount_id: Mapped[int] = ForeignKey("serviceAccounts.id", ondelete='SET NULL')
    platform_id: Mapped[int] = ForeignKey("platforms.id", ondelete="CASCADE")


class AbsoluteStatsModel(Base):
    __tablename__ = "absoluteStats"
    likes_count: Mapped[int]
    views_count: Mapped[int]
    participants_count: Mapped[int]
    repost_count: Mapped[int]
    comms_count: Mapped[int]
    coverage: Mapped[int]
    last_updated_at: Mapped[updated_at]
    group_id: Mapped[int] = ForeignKey("groups.id", ondelete='CASCADE')


class SnapshotModel(Base):
    __tablename__ = "snapshot"

    last_message_id: Mapped[int]
    timestamp: Mapped[created_at]
    type: Mapped[SnapshotType]
    group_id: Mapped[int] = ForeignKey("groups.id", ondelete='CASCADE')


class SnapshotStatsModel(Base):
    __tablename__ = "snapshotStats"

    likes_count: Mapped[int]
    views_count: Mapped[int]
    participants_count: Mapped[int]
    repost_count: Mapped[int]
    comms_count: Mapped[int]
    coverage: Mapped[int]
    snapshot_id: Mapped[int] = ForeignKey("snapshots.id", ondelete="CASCADE")


class ReportModel(Base):
    __tablename__ = "reports"

    filename: Mapped[str_256]
    path: Mapped[str_512]
    compilation_date: Mapped[today]
    filetype: Mapped[FileType]

    group_id: Mapped[int] = ForeignKey("groups.id", ondelete='CASCADE')


class PlatformModel(Base):
    __tablename__ = "platforms"

    name: Mapped[str_128]


class ServiceAccountModel(Base):
    __tablename__ = "serviceAccounts"
    link: Mapped[str_256]
    name: Mapped[str_128]
    platform_id: Mapped[int] = ForeignKey("platforms.id", ondelete="CASCADE")


class ServiceAccountDataModel(Base):
    __tablename__ = "serviceAccountData"

    service_key: Mapped[Optional[str_256]]
    protected_key: Mapped[Optional[str_256]]
    phone_number: Mapped[Optional[str_16]]

    serviceAccount_id: Mapped[int] = ForeignKey("serviceAccounts.id", ondelete='CASCADE')
