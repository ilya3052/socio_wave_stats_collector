from sqlalchemy import select

from src.models import GroupModel, AbsoluteStatsModel, SnapshotModel, PlatformModel, ServiceAccountModel, \
    ServiceAccountDataModel, SnapshotStatsModel
from .base import BaseRepository, T


class GroupsRepository(BaseRepository[GroupModel]):
    def __init__(self, session):
        super().__init__(session, GroupModel)

    def get_groups_by_platform(self, platform_id):
        return self.session.scalars(select(self.model, platform_id)).all()


class AbsoluteStatsRepository(BaseRepository[AbsoluteStatsModel]):
    def __init__(self, session):
        super().__init__(session, AbsoluteStatsModel)

    def get_by_group(self, group_id) -> T:
        return self.session.scalars(select(self.model, group_id)).one()


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


class ServiceAccountDataRepository(BaseRepository[ServiceAccountDataModel]):
    def __init__(self, session):
        super().__init__(session, ServiceAccountDataModel)
