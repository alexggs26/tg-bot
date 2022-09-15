from requests import Timeout, ConnectionError, get
from json import dumps
from tg_bot.app.config import NAVIXY_LOGIN, NAVIXY_PW


def get_hash():
    try:
        response = get(
            url=f'https://panel.navixy.ru/api-v2/panel/account/auth/?login={NAVIXY_LOGIN}&password={NAVIXY_PW}',
            headers={'Content-Type': 'application/json'}
        )


    except Timeout:
        message = f'Ошибка соединения: превышено время ожидания сервера'
        return message

    except ConnectionError:
        message = f'Ошибка соединения: - {ConnectionError}'
        return message

    else:
        response = response.json()
        if response['success'] == False:
            code = response['status']['code']
            description = response['status']['description']
            message = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code}, описание: {description}'
            return message

        else:
            hash = response['hash']
            return hash
