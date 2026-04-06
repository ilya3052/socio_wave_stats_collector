from datetime import datetime

from src.core import create_tables, Session
from src.models import PlatformSchema, PlatformModel, ServiceAccountSchema, ServiceAccountModel, GroupSchema, \
    GroupModel, ServiceAccountDataSchema, ServiceAccountDataModel
from src.repositories import PlatformRepository, ServiceAccountRepository, GroupsRepository, \
    ServiceAccountDataRepository


async def create_basic_elem():
    create_tables()
    with Session() as session:
        repo = PlatformRepository(session)
        platform_vk = PlatformSchema(**{
            "platform_id": 1,
            "platform_name": "ВКонтакте"
        })
        platform_tg = PlatformSchema(**{
            "platform_id": 2,
            "platform_name": "Телеграм"
        })

        repo.add(PlatformModel(**platform_vk.model_dump()))
        repo.add(PlatformModel(**platform_tg.model_dump()))
        repo.commit()

        repo = ServiceAccountRepository(session)
        sacc_vk = ServiceAccountSchema(**{
            "serviceAccount_id": 1,
            "serviceAccount_link": 'https://link.ru',
            "serviceAccount_name": 'SocialPulse',
            "platform_id": 1
        })
        sacc_tg = ServiceAccountSchema(**{
            "serviceAccount_id": 2,
            "serviceAccount_link": 'https://link.ru',
            "serviceAccount_name": 'SocialPulse',
            "platform_id": 2
        })
        # sacc_tg2 = ServiceAccountSchema(**{
        #     "serviceAccount_id": 3,
        #     "serviceAccount_link": 'https://link.ru',
        #     "serviceAccount_name": 'SocialPulse',
        #     "platform_id": 2
        # })
        repo.add(ServiceAccountModel(**sacc_vk.model_dump()))
        repo.add(ServiceAccountModel(**sacc_tg.model_dump()))
        # repo.add(ServiceAccountModel(**sacc_tg2.model_dump()))
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
        group_tg = GroupSchema(**{
            "group_id": 2,
            "group_externalID": 1397484238,
            "group_name": "Липецкий Политех (ЛГТУ)",
            "group_link": "https://t.me/infolgtu",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 2,
            "platform_id": 2
        })
        group_tg2 = GroupSchema(**{
            "group_id": 3,
            "group_externalID": 1135818819,
            "group_name": "КБ",
            "group_link": "https://t.me/Cbpub",
            "group_addedAt": datetime.now().date(),
            "serviceAccount_id": 2,
            "platform_id": 2
        })
        # group_tg3 = GroupSchema(**{
        #     "group_id": 4,
        #     "group_externalID": 1397484236,
        #     "group_name": "Липецкий Политех (ЛГТУ)",
        #     "group_link": "https://t.me/infolgtu",
        #     "group_addedAt": datetime.now().date(),
        #     "serviceAccount_id": 3,
        #     "platform_id": 2
        # })
        repo.add(GroupModel(**group_vk.model_dump()))
        repo.add(GroupModel(**group_tg.model_dump()))
        repo.add(GroupModel(**group_tg2.model_dump()))
        # repo.add(GroupModel(**group_tg3.model_dump()))
        repo.commit()

        repo = ServiceAccountDataRepository(session)
        data_vk = ServiceAccountDataSchema(**{
            "serviceAccountData_id": 1,
            "serviceAccountData_serviceKey": '123',
            "serviceAccountData_protectedKey": '123',
            "serviceAccount_id": 1
        })
        data_tg1 = ServiceAccountDataSchema(**{
            "serviceAccountData_id": 2,
            "serviceAccountData_phoneNumber": '+7(999)999-99-99',
            "serviceAccountData_sessionPath": 'src/sessions/anon.session',
            "serviceAccount_id": 2,
        })
        # data_tg2 = ServiceAccountDataSchema(**{
        #     "serviceAccountData_id": 3,
        #     "serviceAccountData_phoneNumber": '+7(999)999-99-98',
        #     "serviceAccount_id": 3
        # })
        repo.add(ServiceAccountDataModel(**data_vk.model_dump()))
        repo.add(ServiceAccountDataModel(**data_tg1.model_dump()))
        # repo.add(ServiceAccountDataModel(**data_tg2.model_dump()))
        repo.commit()
