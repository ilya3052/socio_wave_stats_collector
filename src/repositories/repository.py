from src.models import GroupModel, AbsoluteStatsModel, SnapshotModel, ReportModel, PlatformModel, ServiceAccountModel, \
    ServiceAccountDataModel
from .base import BaseRepository


class GroupsRepository(BaseRepository[GroupModel]):
    def __init__(self, session):
        super().__init__(session, GroupModel)


class AbsoluteStatsRepository(BaseRepository[AbsoluteStatsModel]):
    def __init__(self, session):
        super().__init__(session, AbsoluteStatsModel)


class SnapshotRepository(BaseRepository[SnapshotModel]):
    def __init__(self, session):
        super().__init__(session, SnapshotModel)


class ReportRepository(BaseRepository[ReportModel]):
    def __init__(self, session):
        super().__init__(session, ReportModel)


class PlatformRepository(BaseRepository[PlatformModel]):
    def __init__(self, session):
        super().__init__(session, PlatformModel)


class ServiceAccountRepository(BaseRepository[ServiceAccountModel]):
    def __init__(self, session):
        super().__init__(session, ServiceAccountModel)


class ServiceAccountDataRepository(BaseRepository[ServiceAccountDataModel]):
    def __init__(self, session):
        super().__init__(session, ServiceAccountDataModel)
