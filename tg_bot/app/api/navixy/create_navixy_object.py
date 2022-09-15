from requests import Timeout, ConnectionError, post
from json import dumps
from tg_bot.app.api.navixy.get_panel_hash import get_hash



def get_backend_hash(client_sys_id):
    panel_hash = get_hash()
    if 'Ошибка' in panel_hash:
        return panel_hash
    else:
        try:
            params = {
                'hash': f"{panel_hash}",
                'user_id': client_sys_id
            }
            backend_hash = post(
                url='https://panel.navixy.ru/api-v2/panel/user/session/create',
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
            backend_hash = backend_hash.json()

            if backend_hash['success'] == 'false':
                code = backend_hash['status']['code']
                description = backend_hash['status']['description']
                message = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code}, описание: {description}'
                return message

            else:
                backend_hash = backend_hash['hash']
                return backend_hash


def create_navixy_object(client_sys_id, device_id, label, model, phone_device):
    backend_hash = get_backend_hash(client_sys_id) # обработать ошибку
    data = {
        "hash": f"{backend_hash}",
        "label": label,
        "group_id": 0,
        "plugin_id": 44,
        "model": model,
        "device_id": device_id,
        "phone": phone_device,
        "send_register_command": True
    }
    if 'satsol' in model:
        data["register_fields"] = {"satsol_password": 1234}

    try:
        response = post(
            url='https://backend.navixy.ru/api-v2/tracker/register',
            headers={'Content-Type': 'application/json'},
            data=dumps(data)
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

            if 'errors' in response:
                description = response['errors']['error']

            else:
                description = response['status']['description']

            message = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code}, описание: {description}'
            return message
        
        else:
            label = response['value']['label']
            message = f'Объект {label} создан, получаю информацию'
            return message
