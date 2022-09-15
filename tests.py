from requests import Timeout, ConnectionError, post, get as requests_get
from tg_bot.app.api.wialon.get_sid import get_sid
from tg_bot.app.api.navixy.get_panel_hash import get_hash
from json import dumps



sys_client_id = 18149513
sid = get_sid('stavros')
item_id = 25794012

# data = {
#     'creatorId': sid['creator_id'],
#     'name': 'telegram_bot-111112',
#     'hwTypeId': 16380891,
#     'dataFlags': 1
# }


# response = post(
#     url='https://hst-api.wialon.com/wialon/ajax.html?svc=core/create_unit',
#     headers={"content-type": "application/x-www-form-urlencoded"},
#     data={"params": dumps(data), "sid": sid['sid']}
# )

# print(response.json())


# data_update = {
#     'itemId': 25794104,
#     'deviceTypeId': 16380891,
#     'uniqueId': 111112
# }

# sid = sid['sid']
# response_update = requests_get(
#     url='https://hst-api.wialon.com/wialon/ajax.html?svc=unit/update_device_type',
#     headers={"content-type": "application/x-www-form-urlencoded"},
#     data={"params": dumps(data_update), "sid": sid}
# )
# print(response_update.json())


headers = {"content-type": "application/x-www-form-urlencoded"}
params_dict_token = {"token": f"d7699ff539e380a4f13e061959377bf450C5A21BF3C93259CDFB56D3BBDB0E6BCAA95BDC"}

response_sid = requests_get(
    url='https://hst-api.wialon.com/wialon/ajax.html?svc=token/login',
    headers=headers,
    params={"params": json.dumps(params_dict_token)}
)

response_sid = response_sid.json()
sid = response_sid['eid']

flags = 1
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

response_objects = requests_get(
    url='https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_items',
    headers=headers,
    params={"params": dumps(params_dict_objects), "sid": sid}
)

response_objects = response_objects.json()['items']
