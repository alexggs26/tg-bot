from tg_bot.app.api.wialon.get_sid import get_sid
from requests import Timeout, ConnectionError, post, get as requests_get
from json import dumps



def create_wialon_object(label, model, client_platform):
    sid = get_sid(client_platform)
    data = {
        'creatorId': sid['creator_id'],
        'name': label,
        'hwTypeId': model,
        'dataFlags': 1
    }
    if 'Ошибка' in sid:
        return sid

    else:
        try:
            response = post(
                url='https://hst-api.wialon.com/wialon/ajax.html?svc=core/create_unit',
                headers={"content-type": "application/x-www-form-urlencoded"},
                data={"params": dumps(data), "sid": sid['sid']}
            )
        except Timeout:
            message = f'Ошибка соединения: превышено время ожидания сервера'
            return message

        except ConnectionError:
            message = f'Ошибка соединения: - {ConnectionError}'
            return message

        else:
            response = response.json()
            if 'error' in response:
                if response['error'] in [1, 7, 8]:
                    message = f"""Ошибка платформы мониторинга Online.Stavrack - доступ запрещен.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                    return message

                if response['error'] in [5, 6]:
                    message = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса.\nПожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                    return message

                if response['error'] == 1002:
                    message = f"""Ошибка платформы мониторинга Online.Stavrack №1002 - Элемент с таким ID зарегистрирован в другом сервисе.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                    return message
                
            else:
                new_object_id = response['item']['id']    
                return new_object_id


def update_device_id(new_object_id, device_id, model, client_platform):
    sid = get_sid(client_platform)
    sid = sid['sid']
    data_update = {
        'itemId': new_object_id,
        'deviceTypeId': model,
        'uniqueId': str(device_id)
    }   
    try:
        response_update = requests_get(
            url='https://hst-api.wialon.com/wialon/ajax.html?svc=unit/update_device_type',
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={"params": dumps(data_update), "sid": sid}
        )
        response_update = response_update.json()
    except Timeout:
            message = f'Ошибка соединения: превышено время ожидания сервера'
            return message

    except ConnectionError:
        message = f'Ошибка соединения: - {ConnectionError}'
        return message 

    else:
        if 'error' in response_update:

            if response_update['error'] in [1, 7, 8]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - доступ запрещен.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                return message

            if response_update['error'] in [5, 6]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса.\nПожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                return message

            if response_update['error'] == 1002:
                message = f"""Ошибка платформы мониторинга Online.Stavrack №1002 - Элемент с таким ID зарегистрирован в другом сервисе.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                return message

        else:
            return response_update['uid']


def update_access_item(client_sys_id, item_id, client_platform):
    if client_platform == 'stavros':
        mgr_platfrom = 'stavros_mgr'
    
    elif client_platform == 'stavros2':
        mgr_platfrom = 'stavros_mgr2'

    sid = get_sid(mgr_platfrom)
    sid = sid['sid']
    data_update_item_access = {
        "userId": client_sys_id,
        "itemId": item_id,
        "accessMask": 0x0001 | 0x0002 | 0x0004 |
            0x0010 | 0x1000 | 0x2000 | 0x0100 | 0x0080 |
            0x0100 | 0x0200 | 0x0000400000 | 0x0001000000 |
            0x0002000000 | 0x0010000000 | 0x0020000000 | 0x8000000000
    }
    try:
        response_update_access = post(
            url='https://hst-api.wialon.com/wialon/ajax.html?svc=user/update_item_access',
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={"params": dumps(data_update_item_access), "sid": sid}
        )
    except Timeout:
        message = f'Ошибка соединения: превышено время ожидания сервера'
        return message

    except ConnectionError:
        message = f'Ошибка соединения: - {ConnectionError}'
        return message

    else:
        response_update_access = response_update_access.json()
        if 'error' in response_update_access:

            if response_update_access['error'] in [1, 7, 8]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - доступ запрещен.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                return message

            if response_update_access['error'] in [5, 6]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса.\nПожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                return message

            if response_update_access['error'] == 1002:
                message = f"""Ошибка платформы мониторинга Online.Stavrack №1002 - Элемент с таким ID зарегистрирован в другом сервисе.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                return message

        else:
             message = 'OK'
             return message    


def migrate_object(item_id, client_account_id, client_platform):
    if client_platform == 'stavros':
        mgr_platfrom = 'stavros_mgr'

    elif client_platform == 'stavros2':
        mgr_platfrom = 'stavros_mgr2'

    sid = get_sid(mgr_platfrom)
    sid = sid['sid']
    data_migrate_object = {
        "itemId": item_id,
        "resourceId": client_account_id
    }
    try:
        response_migrate = post(
            url='https://hst-api.wialon.com/wialon/ajax.html?svc=account/change_account',
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={"params": dumps(data_migrate_object), "sid": sid}
        )
    except Timeout:
        message = f'Ошибка соединения: превышено время ожидания сервера'
        return message

    except ConnectionError:
        message = f'Ошибка соединения: - {ConnectionError}'
        return message
    
    else:
        response_migrate = response_migrate.json()

        if 'error' in response_migrate:

            if response_migrate['error'] in [1, 7, 8]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - доступ запрещен.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                return message

            if response_migrate['error'] in [5, 6]:
                message = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса.\nПожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                return message

            if response_migrate['error'] == 1002:
                message = f"""Ошибка платформы мониторинга Online.Stavrack №1002 - Элемент с таким ID зарегистрирован в другом сервисе.\nПожалуйста, оставьте обращение в тех. поддержку!"""
                return message

            else:
                message = f"""Ошибка платформы мониторинга Online.Stavrack №{response_migrate['error']}. \nПожалуйста, оставьте обращение в тех. поддержку!"""
        else:
             message = 'OK'
             return message


def create_wialon_object_wrapper(device_id, label, model, client_sys_id, client_account_id, client_platform):
    item_id = create_wialon_object(label, model, client_platform)
    uid = update_device_id(item_id, device_id, model, client_platform)
    response_update = update_access_item(client_sys_id, item_id, client_platform)
    response_migrate = migrate_object(item_id, client_account_id, client_platform)
    print(response_migrate)

    if 'Ошибка' in str(item_id):
        return item_id
    elif 'Ошибка' in str(uid):
        return uid
    elif 'Ошибка' in str(response_update):
        return response_update
    elif 'Ошибка' in str(response_migrate):
        return response_migrate
    else: 
        message = {'code': 1, 'message': f'Создан объект c ID {device_id}, проверяю подключение...'}
        return message
