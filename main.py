from src.core import create_tables, Session

import asyncio

from src.models import GroupModel
from src.repositories import GroupsRepository


def main():
    with Session() as session:
        repo = GroupsRepository(session)



main()
