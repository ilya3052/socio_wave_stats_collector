from datetime import datetime

from src.core import create_tables, Session
from src.models import PlatformSchema, PlatformModel, ServiceAccountSchema, ServiceAccountModel, GroupSchema, \
    GroupModel, ServiceAccountDataSchema, ServiceAccountDataModel, AbsoluteStatsModel, AbsoluteStatsSchemaCreate
from src.repositories import PlatformRepository, ServiceAccountRepository, GroupsRepository, \
    ServiceAccountDataRepository, AbsoluteStatsRepository


async def create_basic_elem():
    create_tables()
    with Session() as session:
        repo = PlatformRepository(session)
        platform_vk = PlatformSchema(**{
            "platform_id": 1,
            "platform_name": "ВКонтакте",
            "platform_alias": "VK"
        })
        platform_tg = PlatformSchema(**{
            "platform_id": 2,
            "platform_name": "Телеграм",
            "platform_alias": "TG"
        })

        repo.add(PlatformModel(**platform_vk.model_dump()))
        repo.add(PlatformModel(**platform_tg.model_dump()))
        repo.commit()

        repo = ServiceAccountRepository(session)
        sacc_vk = ServiceAccountSchema(**{
            "serviceAccount_id": 1,
            "serviceAccount_name": 'SocialPulse',
            "serviceAccount_is_activated": True,
            "serviceAccount_app_id": 54438538,
            "platform_id": 1
        })
        sacc_vk2 = ServiceAccountSchema(**{
            "serviceAccount_id": 2,
            "serviceAccount_name": 'SocialPulse2',
            "serviceAccount_is_activated": True,
            "serviceAccount_app_id": 54445084,
            "platform_id": 1
        })
        sacc_tg = ServiceAccountSchema(**{
            "serviceAccount_id": 3,
            "serviceAccount_name": 'SocialPulse',
            "serviceAccount_is_activated": True,
            "platform_id": 2
        })

        repo.add(ServiceAccountModel(**sacc_vk.model_dump()))
        repo.add(ServiceAccountModel(**sacc_vk2.model_dump()))
        repo.add(ServiceAccountModel(**sacc_tg.model_dump()))
        repo.commit()

        repo = GroupsRepository(session)
        group_vk = GroupSchema(**{
            "group_id": 1,
            "group_externalID": 114911631,
            "group_name": "Липецкий Политех (ЛГТУ)",
            "group_link": "https://vk.ru/infolgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 1,
            "platform_id": 1
        })
        group_vk2 = GroupSchema(**{
            "group_id": 2,
            "group_externalID": 61580871,
            "group_name": "Кафедра АСУ ЛГТУ - Официальная группа",
            "group_link": "https://vk.ru/asu.lgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 2,
            "platform_id": 1
        })
        group_vk3 = GroupSchema(**{
            "group_id": 3,
            "group_externalID": 191559812,
            "group_name": "Аниме магазин Maneki (Липецк)",
            "group_link": "https://vk.ru/maneki48",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 2,
            "platform_id": 1
        })
        group_tg = GroupSchema(**{
            "group_id": 4,
            "group_externalID": 1397484238,
            "group_name": "Липецкий Политех (ЛГТУ)",
            "group_link": "https://t.me/infolgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 3,
            "platform_id": 2
        })

        repo.add(GroupModel(**group_vk.model_dump()))
        repo.add(GroupModel(**group_vk2.model_dump()))
        repo.add(GroupModel(**group_vk3.model_dump()))
        repo.add(GroupModel(**group_tg.model_dump()))
        repo.commit()

        repo = AbsoluteStatsRepository(session)
        repo.add(AbsoluteStatsModel(**AbsoluteStatsSchemaCreate(**{"group_id": 1}).model_dump()))
        repo.add(AbsoluteStatsModel(**AbsoluteStatsSchemaCreate(**{"group_id": 2}).model_dump()))
        repo.add(AbsoluteStatsModel(**AbsoluteStatsSchemaCreate(**{"group_id": 3}).model_dump()))
        repo.add(AbsoluteStatsModel(**AbsoluteStatsSchemaCreate(**{"group_id": 4}).model_dump()))
        repo.commit()

        repo = ServiceAccountDataRepository(session)
        data_vk = ServiceAccountDataSchema(**{
            "serviceAccountData_id": 1,
            "serviceAccountData_serviceKey": 'b37b1bceb37b1bceb37b1bce66b045b144bb37bb37b1bceda04751ed922c3191f19eaad',
            "serviceAccountData_protectedKey": 'chq1b4w5YPy71LuKFX70',
            "serviceAccount_id": 1
        })
        data_vk2 = ServiceAccountDataSchema(**{
            "serviceAccountData_id": 2,
            "serviceAccountData_serviceKey": '236bc685236bc685236bc6856c205502992236b236bc6854aec6189447cb332c4bbfd8b',
            "serviceAccountData_protectedKey": 'LvuSPkzu3Yc61C6vvVxe',
            "serviceAccount_id": 2
        })
        data_tg = ServiceAccountDataSchema(**{
            "serviceAccountData_id": 3,
            "serviceAccountData_phoneNumber": '79205189704',
            "serviceAccountData_sessionPath": 'sessions/79205189704.session',
            "serviceAccount_id": 3,
        })

        repo.add(ServiceAccountDataModel(**data_vk.model_dump()))
        repo.add(ServiceAccountDataModel(**data_vk2.model_dump()))
        repo.add(ServiceAccountDataModel(**data_tg.model_dump()))
        repo.commit()
