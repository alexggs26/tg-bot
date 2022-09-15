from requests import Timeout, ConnectionError, post, get
from json import dumps
from tg_bot.loader import bot
from tg_bot.app.api.wialon.get_sid import get_sid
from datetime import datetime



def wialon_get_object_info(device_id, account):

    response_sid = get_sid(account)

    if 'Ошибка' in response_sid:
        message = response_sid
        return message
    else:
        try:
            sid = response_sid['sid']
            base_props = 1
            added_props = 256
            last_message = 1024
            flags = base_props | added_props | last_message

            headers = {"content-type": "application/x-www-form-urlencoded"}

            params = {
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_unique_id",
                    "propValueMask": f"{str(device_id)}",
                    "sortType": "sys_unique_id",
                    "propType": "property",
                    "or_logic": 0
                },
                "force": 1,
                "flags": flags,
                "from": 0,
                "to": 0
            }
            response = post(
                url='https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_items',
                headers=headers,
                data={"params": dumps(params), "sid": sid}
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
            response = response.json()
            if 'error' in response:
                if response['error'] in [1, 7, 8]:
                    description = f"""Ошибка платформы мониторинга Online.Stavrack - доступ запрещен. 
                    Пожалуйста, оставьте обращение в тех. поддержку!"""
                    message = {'code': 'platform_error', 'description': description}
                    return message

                if response['error'] in [5, 6]:
                    description = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса. 
                    Пожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                    message = {'code': 'platform_error', 'description': description}
                    return message

                if response['error'] == 1002:
                    description = f"""Ошибка платформы мониторинга Online.Stavrack №1002 - Элемент с таким ID зарегистрирован в другом сервисе. 
                    Пожалуйста, оставьте обращение в тех. поддержку!"""
                    message = {'code': 'platform_error', 'description': description}
                    return message
                    
            else:
                object_info = response['items']
                if len(object_info) == 0:
                    description = """
                        Объект с таким ID не найден в платформе мониторинга Online.Stavtrack.
                        Для занесения устройства на сервер выберите тип устройства и укажите ID Клиента.
                    """
                    message = {'code': 'not_exist', 'description': description}
                    return message
                else:
                    object_info = object_info[0]
                    name = object_info['nm']

                    if object_info['lmsg'] != None:
                        lat = object_info['lmsg']['pos']['y']
                        lon = object_info['lmsg']['pos']['x']

                        parameters = dumps(object_info['lmsg']['p'], indent=4, sort_keys=True)
                        date_signal = datetime.utcfromtimestamp(object_info['lmsg']['t']).strftime("%Y-%m-%d %H:%M:%S")
                    
                        url_geocode = 'https://geocode-maps.wialon.com/hst-api.wialon.com/gis_geocode?coords=[{"lon":' + str(lon) + ',"lat":' + str(
                            lat) + '}]&flags=1255211008&uid=' + str(response_sid['creator_id'])
                        try:
                            location = get(
                                url=url_geocode,
                                headers=headers
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
                            if 'error' in location:
                                if location['error'] in [1, 7, 8]:
                                    description = f'Ошибка платформы мониторинга Online.Stavrack - доступ запрещен. Пожалуйста, оставьте обращение в тех. поддержку!'
                                    message = {'code': 'platform_error', 'description': description}
                                    return message

                                if location['error'] in [5, 6]:
                                    description = f"""Ошибка платформы мониторинга Online.Stavrack - ошибка выполнения запроса. 
                                    Пожалуйста, попробуйте позднее либо оставьте обращение в тех. поддержку!"""
                                    message = {'code': 'platform_error', 'description': description}
                                    return message
                                else: 
                                    description = 'Ошибка!'
                                    message = {'code': 'platform_error', 'description': description}
                                    return message
                            else:   
                                location = location[0]
                                code = 'send_data'
                                description = f"""
                                    Информация по объекту с ID {device_id} с платформы Online.Stavtrack:\nИмя объекта: {
                                        name}\nДата и время последнего сообщения: {
                                        date_signal}\nМестоположение: {location}\nПараметры:\n{parameters}
                                """
                                message = {'code': code, 'description': description}
                                return message
                    
                    else:
                        message = {'code': 'no_signal', 'message': f'Объект с ID {device_id} не выходил на связь.'}
                        return message
