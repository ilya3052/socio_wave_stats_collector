import asyncio
import logging
import os
import sys

from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from src.core import Platforms
from src.core import Session, Type
from src.exceptions import GroupsNotFoundError, GroupHandleError, SendingError
from src.logger import configure_logging
from src.repositories import ServiceAccountRepository
from src.tasks import run_processing_tasks, run_sending_tasks
from src.tools import create_basic_elem


logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def get_serv_accounts(platform_id):
    with Session() as session:
        repo = ServiceAccountRepository(session)
        return repo.get_with_groups_by_platform(platform_id)


async def main(platform, _type):
    try:
        logger.info("Запуск сбора статистики")
        logger.info(f"Платформа: {platform} | Тип: {_type}")

        _platform = Platforms(platform)
        stats_type = Type(_type)

        accounts = await get_serv_accounts(_platform.id)
        logger.info(f"Найдено сервисных аккаунтов: {len(accounts)} (групп: {sum(len(acc.groups) for acc in accounts)})")

        options = {'platform': Platforms(platform), 'Type': stats_type}

        processing_tasks_result = await run_processing_tasks(accounts, **options)
        logger.info("Этап обработки статистики завершён")

        sending_tasks_result = await run_sending_tasks(processing_tasks_result, stats_type)
        if not all(sending_tasks_result):
            raise SendingError('Произошла ошибка при отправке данных в БД')
        logger.info("Сбор и отправка статистики завершены успешно")

    except (ValidationError, ValueError, GroupsNotFoundError, GroupHandleError, NoResultFound, SendingError):
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
        if len(sys.argv) == 1 or sys.argv[1].lstrip('-') in ('h', 'help'):
            print_help()
            sys.exit(0)

        if sys.argv[1].lstrip('-') in ('create-tables', 'ct'):
            configure_logging()
            logger.info("Запущено создание/пересоздание таблиц в базе данных")
            asyncio.run(create_basic_elem())
            logger.info("Таблицы успешно созданы")
        else:
            configure_logging(sys.argv[1].lstrip('-'))
            asyncio.run(main(sys.argv[1], sys.argv[2].lstrip('-')))

    except KeyboardInterrupt:
        logger.warning("Программа прервана пользователем во время выполнения (KeyboardInterrupt)")
    except ValidationError as VE:
        print(VE)
    except ValueError as VE:
        print(VE)
    except GroupsNotFoundError as GnFE:
        print(GnFE)
    except GroupHandleError as GHE:
        print(GHE)
    except SendingError as SE:
        print(SE)
    except NoResultFound as NRF:
        print(NRF)
    except Exception as e:
        logger.exception("НЕОБРАБОТАННОЕ ИСКЛЮЧЕНИЕ")
        print(e)
    else:
        logger.info("main.py завершён без ошибок")
