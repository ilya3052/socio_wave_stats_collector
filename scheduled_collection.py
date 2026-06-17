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

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def get_serv_accounts(platform_id):
    with Session() as session:
        repo = ServiceAccountRepository(session)
        return repo.get_with_groups_by_platform(platform_id)


async def start_collecting_statistics(platform, _type):
    try:
        logger.info("Запуск сбора статистики")
        logger.info(f"Платформа: {platform} | Тип: {_type}")

        _platform = Platforms(platform)
        stats_type = Type(_type)
        if stats_type == Type.ABSOLUTE:
            logger.error('Неверно указан тип собираемой статистики')
            raise ValueError('Неверно указан тип собираемой статистики')
        accounts = await get_serv_accounts(_platform.id)
        logger.info(f"Найдено сервисных аккаунтов: {len(accounts)} (групп: {sum(len(acc.groups) for acc in accounts)})")
        options = {'platform': Platforms(platform), 'Type': stats_type}

        processing_tasks_result = await run_processing_tasks(accounts, **options)
        logger.info("Этап обработки статистики завершён")

        sending_tasks_result = await run_sending_tasks(processing_tasks_result, stats_type)
        successful_sends = sum(1 for r in sending_tasks_result if not isinstance(r, Exception))
        logger.info(f"Успешно отправлено: {successful_sends} из {len(sending_tasks_result)}")

    except (ValidationError, ValueError, GroupsNotFoundError, GroupHandleError, NoResultFound, SendingError):
        raise


def scheduled_collection():
    """
    ИСПОЛЬЗОВАНИЕ
    main.py <command> [options]
КОМАНДЫ
    vk                      Сбор статистики групп ВКонтакте
    tg                      Сбор статистики каналов Телеграм
ОПЦИИ
    --top                   Обновление недельного топа постов
    --daily                 Сбор статистики за последние сутки
    --hourly                Сбор статистики за последние два часа
    -h --help               Показать эту подсказку
ПРИМЕРЫ
    main.py vk --daily
    """
    try:
        if len(sys.argv) == 1 or sys.argv[1].lstrip('-') in ('h', 'help'):
            print(scheduled_collection.__doc__)
            sys.exit(0)

        else:
            configure_logging(sys.argv[1].lstrip('-'))
            asyncio.run(start_collecting_statistics(sys.argv[1], sys.argv[2].lstrip('-')))

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
        logger.info("Сбор статистики завершён")


if __name__ == "__main__":
    scheduled_collection()
