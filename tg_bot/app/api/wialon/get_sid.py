from requests import Timeout, ConnectionError, post
from json import dumps
from tg_bot.app.dbworker import Storage


def get_sid(account):
    token = Storage.get_token(account)
    headers = {"content-type": "application/x-www-form-urlencoded"}
    params_dict_token = {"token": f"{token}"}
    
    try:
        response = post(
            url='https://hst-api.wialon.com/wialon/ajax.html?svc=token/login',
            headers=headers,
            data={"params": dumps(params_dict_token)}
        )
        response = response.json()

    except Timeout:
        message = f'Ошибка соединения: превышено время ожидания сервера'
        return message

    except ConnectionError:
        message = f'Ошибка соединения: - {ConnectionError}'
        return message
    
    else:
        if 'error' in response:
            if response['error'] in [1, 7, 8]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - доступ запрещен. 
                Пожалуйста, оставьте обращение в тех. поддержку!"""
                return message

            if response['error'] in [5, 6]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса. 
                Пожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                return message

            if response['error'] == 1002:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - Элемент с таким уникальным свойством зарегистрирован в другом сервисе. 
                Пожалуйста, оставьте обращение в тех. поддержку!"""
                return message
        else:
            message = {'sid': response['eid'], 'creator_id': response['user']['id']}
            return message
