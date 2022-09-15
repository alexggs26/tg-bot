from requests import Timeout, ConnectionError, post
from json import dumps
from pandas import DataFrame
from tg_bot.app.config import NAVIXY_LOGIN, NAVIXY_PW


def get_hash():
    data = {
        "login": NAVIXY_LOGIN,
        "password": NAVIXY_PW
    }
    try:
        response = post(
            url='https://panel.navixy.ru/api-v2/panel/account/auth/',
            headers={'Content-Type': 'application/json'},
            data=dumps(data)
        )
        response = response.json()

    except Timeout:
        message = f'Ошибка соединения: превышено время ожидания сервера'
        return message

    except ConnectionError:
        message = f'Ошибка соединения: - {ConnectionError}'
        return message

    else:
        if response['success'] == 'false':
            code = response['status']['code']
            description = response['status']['description']
            message = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code}, описание: {description}'
            return message

        else:
            hash = response['hash']
            return hash


def get_models_list(user_id):
    hash = get_hash()
    data = {
        'hash': f"{hash}",
        'user_id': f"{user_id}"
    }

    response = post(
        url='https://panel.navixy.ru/api-v2/panel/user/session/create',
        headers={'Content-Type': 'application/json'},
        data=dumps(data)
    )
    user_hash = response.json()['hash']
    print('user_hash: ', user_hash)
    data_hash = {
        'hash': f"{user_hash}"
    }
    response = post(
        url='https://backend.navixy.ru/api-v2/tracker/list_models',
        headers={'Content-Type': 'application/json'},
        data=dumps(data_hash)
    )
    response = response.json()['list']
    df = DataFrame(response)
    df.to_excel('nav_eq.xlsx')


get_models_list(20000362)
