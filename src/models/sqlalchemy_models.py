from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional, Dict, Any, List

from sqlalchemy import String, text, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.core import SnapshotType, BestPostInfoType

int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

today = Annotated[datetime, mapped_column(server_default=text("CURRENT_DATE"))]

str_11 = Annotated[str, 11]
str_16 = Annotated[str, 16]
str_128 = Annotated[str, 128]
str_150 = Annotated[str, 150]
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
        str_11: String(11),
        str_16: String(16),
        str_128: String(128),
        str_150: String(150),
        str_256: String(256),
        str_512: String(512)
    }


class UsersModel(Base, TypesMixin):
    __tablename__ = "users_customuser"
    email: Mapped[str_128]
    is_email_confirmed: Mapped[bool]


class GroupUsersModel(Base):
    __tablename__ = "social_entities_group_users"
    group_id: Mapped[int] = mapped_column(
        ForeignKey("social_entities_group.id", ondelete="CASCADE")
    )
    customuser_id: Mapped[int] = mapped_column(
        ForeignKey("users_customuser.id", ondelete="CASCADE")
    )
    __table_args__ = (
        UniqueConstraint("group_id", "customuser_id", name="uq_group_user"),
    )


class GroupModel(Base, TypesMixin):
    __tablename__ = "social_entities_group"
    external_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str_128]
    link: Mapped[str_256]
    added_at: Mapped[created_at]
    status: Mapped[str_128]
    slug: Mapped[str_128]

    service_account_id: Mapped[int] = mapped_column(
        ForeignKey("service_accounts_serviceaccount.id", ondelete='SET NULL'))
    service_account: Mapped['ServiceAccountModel'] = relationship(
        back_populates='groups'
    )
    platform_id: Mapped[int] = mapped_column(ForeignKey("social_entities_platform.id", ondelete="CASCADE"))
    platform: Mapped['PlatformModel'] = relationship(back_populates='groups')
    aggregated_post_data: Mapped[Dict[str, Any]] = mapped_column(type_=JSONB)

    stats: Mapped['AbsoluteStatsModel'] = relationship(
        back_populates='group'
    )

    best_posts: Mapped['BestPostInfoModel'] = relationship(
        back_populates='group'
    )

    post_metrics: Mapped['PostMetricsModel'] = relationship(
        back_populates='group'
    )

    users: Mapped[List['UsersModel']] = relationship(
        secondary='social_entities_group_users',
        viewonly=True,
    )

    __table_args__ = (
        UniqueConstraint("platform_id", "external_id", name="uq_group_platform_external"),
    )


class BestPostInfoModel(Base, TypesMixin):
    __tablename__ = "stats_bestpostinfo"
    repr_columns = ('id', 'post_id', 'content',)
    likes_count: Mapped[int]
    reposts_count: Mapped[int]
    comms_count: Mapped[int]
    views_count: Mapped[int]
    content: Mapped[str_150]
    post_id: Mapped[int]
    post_type: Mapped[BestPostInfoType]
    last_updated_at: Mapped[updated_at]

    group_id: Mapped[int] = mapped_column(ForeignKey("social_entities_group.id", ondelete="CASCADE"))
    group: Mapped['GroupModel'] = relationship(back_populates='best_posts')


class AbsoluteStatsModel(Base, TypesMixin):
    __tablename__ = "stats_absolutestats"
    likes_count: Mapped[int]
    views_count: Mapped[int]
    participants_count: Mapped[int]
    repost_count: Mapped[int]
    comms_count: Mapped[int]
    last_updated_at: Mapped[updated_at]
    posts_count: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey("social_entities_group.id", ondelete='CASCADE'))
    group: Mapped['GroupModel'] = relationship(
        back_populates='stats'
    )


class SnapshotModel(Base, TypesMixin):
    __tablename__ = "stats_snapshot"
    repr_columns = ('id',)
    timestamp: Mapped[created_at]
    type: Mapped[SnapshotType]
    group_id: Mapped[int] = mapped_column(ForeignKey("social_entities_group.id", ondelete='CASCADE'))
    stats: Mapped['SnapshotStatsModel'] = relationship(
        back_populates='snapshot'
    )


class SnapshotStatsModel(Base, TypesMixin):
    __tablename__ = "stats_snapshotstats"
    repr_columns = ('id',)
    likes_count: Mapped[int]
    views_count: Mapped[int]
    participants_delta: Mapped[int]
    repost_count: Mapped[int]
    comms_count: Mapped[int]
    ERR: Mapped[Decimal]
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("stats_snapshot.id", ondelete="CASCADE"))
    snapshot: Mapped['SnapshotModel'] = relationship(
        uselist=False,
        back_populates='stats'
    )


class PlatformModel(Base, TypesMixin):
    __tablename__ = "social_entities_platform"

    name: Mapped[str_128]
    alias: Mapped[str_16]
    groups: Mapped[list['GroupModel']] = relationship(back_populates='platform')
    accounts: Mapped[list['ServiceAccountModel']] = relationship(back_populates='platform')


class ServiceAccountModel(Base, TypesMixin):
    __tablename__ = "service_accounts_serviceaccount"
    name: Mapped[str_128]

    platform_id: Mapped[int] = mapped_column(ForeignKey("social_entities_platform.id", ondelete="CASCADE"))
    platform: Mapped['PlatformModel'] = relationship(
        back_populates='accounts'
    )

    app_id: Mapped[Optional[int]] = mapped_column(unique=True, nullable=True)

    is_activated: Mapped[bool] = mapped_column(server_default=text('false'))

    data: Mapped['ServiceAccountDataModel'] = relationship(
        uselist=False,
        back_populates='account'
    )
    groups: Mapped[list['GroupModel']] = relationship(
        back_populates='service_account'
    )


class ServiceAccountDataModel(Base, TypesMixin):
    __tablename__ = "service_accounts_serviceaccountdata"

    service_key: Mapped[Optional[str_256]]
    protected_key: Mapped[Optional[str_256]]
    phone_number: Mapped[Optional[str_11]]
    session_path: Mapped[Optional[str_256]]

    account_id: Mapped[int] = mapped_column(ForeignKey("service_accounts_serviceaccount.id", ondelete='CASCADE'))
    account: Mapped['ServiceAccountModel'] = relationship(back_populates='data')


class PostMetricsModel(Base, TypesMixin):
    __tablename__ = "stats_postmetrics"

    post_id: Mapped[int]
    likes_count: Mapped[int]
    views_count: Mapped[int]
    reposts_count: Mapped[int]
    comms_count: Mapped[int]
    hour: Mapped[int]
    day_of_week: Mapped[int]
    is_weekend: Mapped[bool]
    text_length: Mapped[int]
    like_view_ratio: Mapped[float]
    has_video: Mapped[bool]
    has_photo: Mapped[bool]
    word_count: Mapped[int]

    timestamp: Mapped[datetime]

    group_id: Mapped[int] = mapped_column(ForeignKey("social_entities_group.id", ondelete='CASCADE'))
    group: Mapped['GroupModel'] = relationship(back_populates='post_metrics')
