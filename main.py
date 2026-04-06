import os
import sys
import traceback

from icecream import ic
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.core import Platforms
from src.exceptions import GroupsNotFoundError, GroupHandleError, SendingError
from src.tasks import run_processing_tasks, run_sending_tasks
from src.tools import create_basic_elem

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
    except NoResultFound:
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
        tb_str = ''.join(traceback.format_tb(VE.__traceback__))
        print("Стек\n", tb_str, '=' * 100)
        print(VE)
    except ValueError as VE:
        tb_str = ''.join(traceback.format_tb(VE.__traceback__))
        print("Стек\n", tb_str, '=' * 100)
        print(VE)
    except GroupsNotFoundError as GnFE:
        tb_str = ''.join(traceback.format_tb(GnFE.__traceback__))
        print("Стек\n", tb_str, '=' * 100)
        print(GnFE)
    except GroupHandleError as GHE:
        tb_str = ''.join(traceback.format_tb(GHE.__traceback__))
        print("Стек\n", tb_str, '=' * 100)
        print(GHE)
    except SendingError as SE:
        tb_str = ''.join(traceback.format_tb(SE.__traceback__))
        print("Стек\n", tb_str, '=' * 100)
        print(SE)
    except NoResultFound as NRF:
        tb_str = ''.join(traceback.format_tb(NRF.__traceback__))
        print("Стек\n", tb_str, '=' * 100)
        print(NRF)
