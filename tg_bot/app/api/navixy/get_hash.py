from requests import Timeout, ConnectionError, post
from json import dumps
from tg_bot.app.config import NAVIXY_LOGIN, NAVIXY_PW


def get_hash():
    data = {
        "login": NAVIXY_LOGIN,
        "password": NAVIXY_PW
    }
    try:
        response = post(
            url='https://panel.navixy.ru/api-v2/backend/account/auth/',
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