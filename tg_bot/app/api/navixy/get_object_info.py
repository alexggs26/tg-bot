from requests import Timeout, ConnectionError, post
from json import dumps
from tg_bot.loader import bot
from tg_bot.app.api.navixy.get_panel_hash import get_hash
from datetime import datetime


def navixy_get_panel_info(device_id):
    response_hash = get_hash()
    if 'Ошибка' in response_hash:
        message = response_hash
        return message

    else:
        try:
            """
            Сначала мы должны узнать системный ID трекера для выполнения запроса.
            Для этого мы делаем запрос read_all к panel API и собираем список из словарей sys_id, device_id, user_id 
            """
            hash = response_hash
            dict_params = {
                "hash": f"{hash}",
                "tracker_id": device_id
            }

            tracker_object = post(
                url='https://panel.navixy.ru/api-v2/panel/tracker/list/',
                headers={'Content-Type': 'application/json'},
                data=dumps(dict_params)
            )

        except Timeout:
            description = f'Ошибка соединения: превышено время ожидания сервера'
            message = {'code': 'network_error', 'desctiption': description}
            return message

        except ConnectionError:
            description = f'Ошибка соединения: - {ConnectionError}'
            message = {'code': 'network_error', 'desctiption': description}
            return message
        
        else:
            tracker_object = tracker_object.json()
            if tracker_object['success'] == False:
                if tracker_object['status']['code'] == 201:
                    message = None
                    return message

                else:
                    code_platform = tracker_object['status']['code']
                    description_platform = tracker_object['status']['description']
                    description = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code_platform}, описание: {description_platform}'
                    message = {'code': 'platform_error', 'description': description}
                    return message
            else:
                tracker_info = dict()
                for i in tracker_object['list']:
                    if i['source']['device_id'] == device_id:
                        tracker_info = {
                            'success': True,
                            'sys_id': i['id'],
                            'device_id': i['source']['device_id'],
                            'label': i['label'],
                            'user_id': i['user_id']
                        }
                return tracker_info


def navixy_get_backend_user_hash(device_id):

    tracker_info = navixy_get_panel_info(device_id)
    if tracker_info == None:
        return tracker_info

    if not tracker_info:
        tracker_info = None
        return tracker_info

    else:
        if tracker_info['success'] == True:
            response_hash = get_hash()
            if 'Ошибка' in response_hash:
                message = response_hash
                return message
            else: 
                data={
                    'hash': f"{response_hash}",
                    'user_id': tracker_info['user_id']
                }
                try:
                    user_hash = post(
                        url='https://panel.navixy.ru/api-v2/panel/user/session/create',
                        headers={'Content-Type': 'application/json'},
                        data=dumps(data)
                    )

                except Timeout:
                    description = f'Ошибка соединения: превышено время ожидания сервера'
                    message = {'code': 'network_error', 'desctiption': description}
                    return message

                except ConnectionError:
                    description = f'Ошибка соединения: - {ConnectionError}'
                    message = {'code': 'network_error', 'desctiption': description}
                    return message

                else:
                    user_hash = user_hash.json()
                    if user_hash['success'] == False:
                        if user_hash['status']['code'] == 201:
                            message = None
                            return message
                        else:     
                            code_platform = user_hash['status']['code']
                            description_platform = user_hash['status']['description']
                            description = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code_platform}, описание: {description_platform}'
                            message = {'code': 'platform_error','description': description}
                            return message
                    else:
                        tracker_info['hash'] = user_hash['hash']
                        return tracker_info



async def navixy_get_object_info(device_id):
    """
    Используем user_hash, полученный в navixy_get_backend_user_hash,
    и передаем device_id в метод tracker/get_state
    """

    tracker_info = navixy_get_backend_user_hash(device_id)


    if tracker_info == None:
        description = 'Объект с таким ID не найден в платформе мониторинга My.Stavtrack. Проверяю другую платформу...'
        message = {'code': 'not_exist', 'description': description}
        return message

    else:
        try:
            dict_params = {
                "hash": tracker_info['hash'],
                "tracker_id": tracker_info['sys_id']
            }

            response = post(
                url='https://backend.navixy.ru/api-v2/tracker/get_state',
                headers={'Content-Type': 'application/json'},
                data=dumps(dict_params)
            )

        except Timeout:
            description = f'Ошибка соединения: превышено время ожидания сервера'
            message = {'code': 'network_error',
                'desctiption': description}
            return message

        except ConnectionError:
            description = f'Ошибка соединения: - {ConnectionError}'
            message = {'code': 'network_error', 'desctiption': description}
            return message

        else:
            response = response.json()
            if response['success'] == False:
                if response['status']['code'] == 201:
                    description = 'Объект с таким ID не найден в платформе мониторинга My.Stavtrack. Проверяю другую платформу...'
                    message = {'code': 'not_exist', 'description': description}
                    return message
                else:    
                    code_platform = response['status']['code']
                    description_platform = response['status']['description']
                    description = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code_platform}, описание: {description_platform}'
                    message = {'code': 'platform_error', 'description': description}
                    return message

            else:
                if datetime.strptime(response['state']['gps']['updated'], '%Y-%m-%d %H:%M:%S') > datetime(1970, 1, 1, 0, 0, 0):
                    name = tracker_info['label']
                    date_signal = response['state']['gps']['updated']
                    gps_lat = response['state']['gps']['location']['lat']
                    gps_lon = response['state']['gps']['location']['lng']
                    connection_status = response['state']['connection_status']
                    network_name = response['state']['gsm']['network_name']
                    battery_level = response['state']['battery_level']
                    
                    params = {
                        'hash': tracker_info['hash'],
                        'location': {
                            'lat': gps_lat,
                            'lng': gps_lon
                        },
                        'geocoder': 'yandex',
                        'lang': 'ru',
                        'with_details': False
                    }

                    try:
                        location = post(
                            url='https://panel.navixy.ru/api-v2/geocoder/search_location',
                            headers={'Content-Type': 'application/json'},
                            data=dumps(params)
                    )
                    except Timeout:
                        description = f'Ошибка соединения: превышено время ожидания сервера'
                        message = {'code': 'network_error', 'desctiption': description}
                        return message

                    except ConnectionError:
                        description = f'Ошибка соединения: - {ConnectionError}'
                        message = {'code': 'network_error', 'desctiption': description}
                        return message

                    else:
                        location = location.json()
                        if location['success'] == False:
                            code_platform = location['status']['code']
                            description_platform = location['status']['description']
                            description = f'Ошибка платформы мониторинга My.Stavtrack: - код: {code_platform}, описание: {description_platform}'
                            message = {'code': 'platform_error', 'description': description}
                            return message
                        else:
                            location = location['value']

                        description = f"""Информация по объекту с ID {device_id} с платформы My.Stavtrack:\nМестоположение: {
                            location}\nДата и время последнего сообщения: {
                            date_signal}\n\nИмя объекта: {
                            name}\nСтатус: {connection_status}\nОператор: {
                            network_name}\nЗаряд АКБ: {battery_level}
                        """
                        message = {'code': 'send_data', 'description': description}
                        return message

                else:
                    name = tracker_info['label']
                    date_signal = 'Не выходил на связь'
                    connection_status = response['state']['connection_status']
                    description = f"""Информация по объекту с ID {device_id} с платформы My.Stavtrack:\nИмя объекта: {
                            name}\nДата и время последнего сообщения: {
                            date_signal}\nСтатус: {connection_status}
                        """
                    message = {'code': 'no_signal', 'description': description}
                    return message


                
