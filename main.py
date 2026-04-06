import os
import sys

from pydantic import ValidationError

from src.core.config import Platforms
from src.exceptions.exceptions import GroupsNotFoundError, GroupHandleError, SendingError
from src.tasks import run_processing_tasks, run_sending_tasks
from src.tools.create_basic_elem import create_basic_elem

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio

from src.core import Session, Type

from src.repositories import ServiceAccountRepository


async def get_serv_accounts(platform_id):
    with Session() as session:
        repo = ServiceAccountRepository(session)
        return repo.get_with_groups_by_platform(platform_id)


async def main(platform, _type):
    try:
        _platform = Platforms(platform)
        stats_type = Type(_type)
        accounts = await get_serv_accounts(_platform.id)
        options = {'platform': Platforms(platform), 'Type': stats_type}

        processing_tasks_result = await run_processing_tasks(accounts, **options)

        sending_tasks_result = await run_sending_tasks(processing_tasks_result, stats_type)
        if not all(sending_tasks_result):
            raise SendingError('Произошла ошибка при отправке данных в БД')

    except ValidationError:
        raise
    except ValueError:
        raise
    except GroupsNotFoundError:
        raise
    except GroupHandleError:
        raise


def print_help():
    print("""\
ИСПОЛЬЗОВАНИЕ
    main.py <command> [options]
КОМАНДЫ
    vk             Сбор статистики групп ВКонтакте
    tg              Сбор статистики каналов Телеграм
ОПЦИИ
    --absolute         Сбор полной статистики группы
    --daily            Сбор статистики за последние сутки
    --hourly          Сбор статистики за последние два часа
    -ct --create-tables   Создание таблиц в базе
    -h --help             Показать эту подсказку
ПРИМЕРЫ       
    main.py vkontakte -a
    main.py --create-tables
    """)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1 or (sys.argv[1].lstrip('-')) in ('h', 'help'):
            print_help()
            exit(0)

        if sys.argv[1].lstrip('-') in ('create-tables', 'ct'):
            asyncio.run(create_basic_elem())
        else:
            asyncio.run(main(sys.argv[1], sys.argv[2].lstrip('-')))
    except KeyboardInterrupt:
        print('Заверешение по прерыванию..')
    except ValidationError as VE:
        print(VE, VE.args)
    except ValueError as VE:
        print(VE, VE.args)
    except GroupsNotFoundError as GnFE:
        print(GnFE, GnFE.args)
    except GroupHandleError as GHE:
        print(GHE, GHE.args)
    except SendingError as SE:
        print(SE, SE.args)
