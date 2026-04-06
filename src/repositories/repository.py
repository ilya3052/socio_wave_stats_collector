from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload, joinedload

from src.models import GroupModel, AbsoluteStatsModel, SnapshotModel, PlatformModel, ServiceAccountModel, \
    ServiceAccountDataModel, SnapshotStatsModel
from .base import BaseRepository, T


class GroupsRepository(BaseRepository[GroupModel]):
    def __init__(self, session):
        super().__init__(session, GroupModel)

    def get_groups_by_platform(self, platform_id):
        return self.session.scalars(select(self.model).filter_by(platform_id=platform_id)).all()


class AbsoluteStatsRepository(BaseRepository[AbsoluteStatsModel]):
    def __init__(self, session):
        super().__init__(session, AbsoluteStatsModel)

    def get_by_group(self, group_id) -> T:
        try:
            return self.session.scalars(select(self.model).filter_by(group_id=group_id)).one()
        except NoResultFound:
            raise


class SnapshotRepository(BaseRepository[SnapshotModel]):
    def __init__(self, session):
        super().__init__(session, SnapshotModel)


class SnapshotStatsRepository(BaseRepository[SnapshotStatsModel]):
    def __init__(self, session):
        super().__init__(session, SnapshotModel)


class PlatformRepository(BaseRepository[PlatformModel]):
    def __init__(self, session):
        super().__init__(session, PlatformModel)


class ServiceAccountRepository(BaseRepository[ServiceAccountModel]):
    def __init__(self, session):
        super().__init__(session, ServiceAccountModel)

    def get_with_groups_by_platform(self, platform_id):
        return (self.session.scalars(select(self.model)
                                     .filter_by(platform_id=platform_id)
                                     .options(selectinload(ServiceAccountModel.groups))
                                     .options(joinedload(ServiceAccountModel.data)))

                .all())


class ServiceAccountDataRepository(BaseRepository[ServiceAccountDataModel]):
    def __init__(self, session):
        super().__init__(session, ServiceAccountDataModel)
