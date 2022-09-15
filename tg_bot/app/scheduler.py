from logging import getLogger, basicConfig, INFO
from requests import post
from json import dumps
from pandas import DataFrame, concat
from sqlalchemy import create_engine
from pymysql import Error, connect
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import get_event_loop
from tg_bot.app.config import DB_HOST, DB_USER, DB_PW, DB_DATABASE, NAVIXY_LOGIN, NAVIXY_PW
from tg_bot.app.dbworker import Storage




def get_wialon_users():

    base_props = 1
    billing_props = 4
    custom_props = 8
    flags = base_props | billing_props | custom_props


    objects = DataFrame(
        columns=['sys_client_id', 'account_id', 'crm_client_id', 'platform'])

    token_stavros = Storage.get_token('stavros')
    token_stavros2 = Storage.get_token('stavros2')
    tokens = [token_stavros, token_stavros2]

    num = 1
    for token in tokens:
         
        headers = {"content-type": "application/x-www-form-urlencoded"}
        params_dict_token = {"token": f"{token}"}

        response_sid = post(
            url='https://hst-api.wialon.com/wialon/ajax.html?svc=token/login',
            headers=headers,
            data={"params": dumps(params_dict_token)}
        )
        response_sid = response_sid.json()
        sid = response_sid['eid']

        params_dict_objects = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name",
                "propType": "property",
                "or_logic": 0
            },
            "force": 1,
            "flags": flags,
            "from": 0,
            "to": 0
        }

        response_objects = post(
            url='https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_items',
            headers=headers,
            data={"params": dumps(params_dict_objects), "sid": sid}
        )

        response_objects = response_objects.json()['items']
        objects_info = []

        for i in response_objects:
            for j in i.keys():
                if j == 'flds':
                    for l in i[j].keys():
                        for k in i[j][l].values():
                            if k == 'CRM_ID_COMPANY':
                                objects_info.append([
                                    i['crt'],
                                    i['bact'], 
                                    i[j][l]['v'],
                                    'stavros' if num == 1 else 'stavros2'
                                ])

        users_info = DataFrame(objects_info, columns=[
                                 'sys_client_id', 'account_id', 'crm_client_id', 'platform'])

        users = concat([objects, users_info], ignore_index=True)
        users = users.drop_duplicates()
        num = num + 1
        return users


def get_navixy_users():
    data = {
    "login": NAVIXY_LOGIN,
    "password": NAVIXY_PW
    }
    response = post(
        url='https://panel.navixy.ru/api-v2/panel/account/auth/',
        headers={'Content-Type': 'application/json'},
        data=dumps(data)
    )
    hash = response.json()['hash']
    dict_hash = {
        "hash": f"{hash}"
    }
    users = post(
        url='https://panel.navixy.ru/api-v2/panel/user/list/',
        headers={'Content-Type': 'application/json'},
        data=dumps(dict_hash)
    )
    users = users.json()['list']
    users_list = []

    for i in users:
        users_list.append([
            i['id'],
            None,
            i['login'],
            'navixy'
        ]
        )
    users_df = DataFrame(users_list, columns=[
                         'sys_client_id', 'account_id', 'crm_client_id', 'platform'])
    return users_df


def push_users():
    users_wialon = get_wialon_users()
    users_navixy = get_navixy_users()

    users = DataFrame(
        columns=['sys_client_id', 'account_id', 'crm_client_id', 'platform'])
    
    users = concat([users, users_wialon], ignore_index=True)
    users = concat([users, users_navixy], ignore_index=True)

    connection_string = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}/{DB_DATABASE}')

    con = connect(
        host=DB_HOST, 
        user=DB_USER,
        password=DB_PW,
        database=DB_DATABASE
    )
    query = 'truncate smt_clients'
    try:
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        users.to_sql(con=connection_string, name='smt_clients', if_exists='append', index=False)
    except Error as e:
        print(e) 
    finally:
        cursor.close()
        con.close()



def job():
    push_users()
    return None

job()
# logger = getLogger(__name__)

# basicConfig(
#     level=INFO,
#     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     filename="scheduler.log"
# )
# logger.error("Starting bot")

# scheduler = AsyncIOScheduler()
# scheduler.add_job(job, "interval", seconds=300)
# scheduler.start()
# get_event_loop().run_forever()
