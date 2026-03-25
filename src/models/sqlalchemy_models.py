from datetime import datetime
from enum import StrEnum
from typing import Annotated, Optional

from sqlalchemy import String, text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.core.config import SnapshotType

int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

today = Annotated[datetime, mapped_column(server_default=text("CURRENT_DATE"))]

str_16 = Annotated[str, 16]
str_128 = Annotated[str, 128]
str_256 = Annotated[str, 256]
str_512 = Annotated[str, 512]


class Base(DeclarativeBase):
    id: Mapped[int_pk]
    repr_cols_num = 3
    repr_columns = ()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_columns or idx < self.repr_cols_num:
                cols.append(f"{col} = {getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class TypesMixin:
    type_annotation_map = {
        str_16: String(16),
        str_128: String(128),
        str_256: String(256),
        str_512: String(512)
    }


class GroupModel(Base, TypesMixin):
    __tablename__ = "groups"
    external_id: Mapped[int]
    name: Mapped[str_128]
    link: Mapped[str_256]
    added_at: Mapped[created_at]
    serviceAccount_id: Mapped[int] = mapped_column(ForeignKey("serviceAccounts.id", ondelete='SET NULL'))
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id", ondelete="CASCADE"))
    platform: Mapped['PlatformModel'] = relationship(back_populates='groups')

    stats: Mapped['AbsoluteStatsModel'] = relationship(
        uselist=False,
        back_populates='group'
    )

    __table_args__ = (
        UniqueConstraint("platform_id", "external_id", name="uq_group_platform_external"),
    )


class AbsoluteStatsModel(Base, TypesMixin):
    __tablename__ = "absoluteStats"
    likes_count: Mapped[int]
    views_count: Mapped[int]
    participants_count: Mapped[int]
    repost_count: Mapped[int]
    comms_count: Mapped[int]
    last_updated_at: Mapped[updated_at]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete='CASCADE'))
    group: Mapped['GroupModel'] = relationship(
        back_populates='stats'
    )


class SnapshotModel(Base, TypesMixin):
    __tablename__ = "snapshot"
    repr_columns = ('id',)
    last_message_id: Mapped[int]
    timestamp: Mapped[created_at]
    type: Mapped[SnapshotType]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete='CASCADE'))
    stats: Mapped['SnapshotStatsModel'] = relationship(
        back_populates='snapshot'
    )


class SnapshotStatsModel(Base, TypesMixin):
    __tablename__ = "snapshotStats"
    repr_columns = ('id',)
    likes_count: Mapped[int]
    views_count: Mapped[int]
    participants_delta: Mapped[int]
    repost_count: Mapped[int]
    comms_count: Mapped[int]
    coverage: Mapped[int]
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshot.id", ondelete="CASCADE"))
    snapshot: Mapped['SnapshotModel'] = relationship(
        uselist=False,
        back_populates='stats'
    )


class PlatformModel(Base, TypesMixin):
    __tablename__ = "platforms"

    name: Mapped[str_128]

    groups: Mapped[list['GroupModel']] = relationship(back_populates='platform')


class ServiceAccountModel(Base, TypesMixin):
    __tablename__ = "serviceAccounts"
    link: Mapped[str_256]
    name: Mapped[str_128]
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id", ondelete="CASCADE"))
    data: Mapped['ServiceAccountDataModel'] = relationship(
        uselist=False,
        back_populates='serviceAccount'
    )


class ServiceAccountDataModel(Base, TypesMixin):
    __tablename__ = "serviceAccountData"

    service_key: Mapped[Optional[str_256]]
    protected_key: Mapped[Optional[str_256]]
    phone_number: Mapped[Optional[str_16]]

    serviceAccount_id: Mapped[int] = mapped_column(ForeignKey("serviceAccounts.id", ondelete='CASCADE'))
    serviceAccount: Mapped['ServiceAccountModel'] = relationship(back_populates='data')
