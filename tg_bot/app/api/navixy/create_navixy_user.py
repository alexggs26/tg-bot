from requests import Timeout, ConnectionError, post
from json import dumps
from tg_bot.app.api.navixy.get_panel_hash import get_hash


def create_user(client_id):
    response_hash = get_hash()
    if 'Ошибка' in response_hash:
        message = response_hash
        return message
    else:
        try:     
            params = {
                "hash": f'{response_hash}',
                "user": {
                    "activated": True,
                    "verified": True,
                    "login": f"{client_id}@st.ru",
                    "first_name": f"{client_id}",
                    "middle_name": f"{client_id}",
                    "last_name": f"{client_id}",
                    "legal_name": "-",
                    "legal_type": "legal_entity",
                    "phone": "",
                    "post_country": "-",
                    "post_index": "-",
                    "post_region": "-",
                    "post_city": "-", 
                    "post_street_address": "-",
                    "registered_country": "-",
                    "registered_index": "-",
                    "registered_region": "-",
                    "registered_city": "-",
                    "registered_street_address": "-",
                    "state_reg_num": "",
                    "tin": "",
                    "okpo_code": "",
                    "iec": ""
                },
                "time_zone": "Europe/Moscow", 
                "locale": "ru", 
                "password": "123321", 
                "discount": {
                    "value": 0.0, 
                    "min_trackers": 0, 
                    "end_date": None, 
                    "strategy": "sum_with_progressive"
                    }, 
                "comment": "-"
                }
            response = post(
                url='https://panel.navixy.ru/api-v2/panel/user/create',
                headers={'Content-Type': 'application/json'},
                data=dumps(params)
            )
        except Timeout:
            message = f'Ошибка соединения: превышено время ожидания сервера'
            return message

        except ConnectionError:
            message = f'Ошибка соединения: - {ConnectionError}'
            return message
        else:
            response = response.json()
            print(response)
            if response['success'] == False:
                code = response['status']['code']
                description = response['status']['description']
                message = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code}, описание: {description}'
                return message

            else:
                client_sys_id = response['id']
                return client_sys_id