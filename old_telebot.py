import asyncio
import calendar
import json
import time
from threading import Thread

import requests as requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = "1815450153:AAGUIGh5EnSTGcpMzI0nxyu6wOnnljcR_zs"
#TOKEN = "1942789189:AAHqowaf1Y-j4TdUF6J4E_y2cjy0PPQUNkk"
# WIALON_TOKEN = "ec0b0260b7cebfa4a19d0829d6822bc27BA1A5BB4D2F1E63772C307A7C4F950A5EE2B672"
WIALON_TOKEN = ""

bot = Bot(token=TOKEN)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)

sid = ''
creator_id = ''


def get_sid():
    global sid, creator_id
    response = requests.get(
        'https://hst-api.wialon.com/wialon/ajax.html?svc=token/login&params={"token":"' + str(WIALON_TOKEN) + '"}')
    response = response.json()
    if 'error' in response and (response['error'] == 1 or response['error'] == 7 or response['error'] == 4):
        update_wialon_token()
        response = requests.get(
            'https://hst-api.wialon.com/wialon/ajax.html?svc=token/login&params={"token":"' + str(WIALON_TOKEN) + '"}')
        response = response.json()
    sid = response['eid']
    creator_id = response['user']['id']


async def get_object(device_id):
    global sid, creator_id
    response = requests.get(
        'https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_items&params={"spec":{"itemsType":"avl_unit","propName":"sys_unique_id","propValueMask":"' + str(
            device_id) + '","sortType":"sys_name"},"force":1,"flags":1025,"from":0,"to":0}&sid=' + str(sid))
    response = response.json()
    if 'error' in response and (response['error'] == 1 or response['error'] == 7):
        await async_update_wialon_token()
        response = requests.get(
            'https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_items&params={"spec":{"itemsType":"avl_unit","propName":"sys_unique_id","propValueMask":"' + str(
                device_id) + '","sortType":"sys_name"},"force":1,"flags":1025,"from":0,"to":0}&sid=' + str(sid))
        response = response.json()
    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]
    elif 'items' in response and len(response['items']) == 0:
        return None
    else:
        return response


async def create_object(device_id, hw_type_id, msg):
    global sid, creator_id
    response = requests.get(
        'https://hst-api.wialon.com/wialon/ajax.html?svc=core/create_unit&params={"creatorId":' + str(
            creator_id) + ',"name":"' + str(device_id) + '","hwTypeId":' + str(
            hw_type_id) + ',"dataFlags":1}&sid=' + str(sid) + '')
    response = response.json()
    if 'error' in response and (response['error'] == 1 or response['error'] == 7):
        await async_update_wialon_token()
        response = requests.get(
            'https://hst-api.wialon.com/wialon/ajax.html?svc=core/create_unit&params={"creatorId":' + str(
                creator_id) + ',"name":"' + str(device_id) + '","hwTypeId":' + str(
                hw_type_id) + ',"dataFlags":1}&sid=' + str(sid) + '')
        response = response.json()
    if 'error' in response:
        await msg.answer(
            'При запросе в Wialon произошла ошибка. {}'.format(json.dumps(response) if response is not None else ''))
        return None
    new_id = response['item']['id']

    response2 = requests.get(
        'https://hst-api.wialon.com/wialon/ajax.html?svc=unit/update_device_type&params={"itemId":' + str(
            new_id) + ',"deviceTypeId":' + str(hw_type_id) + ',"uniqueId":' + str(
            device_id) + '}&sid=' + str(sid) + '')
    return response2.json()


async def process_device(msg, model_id):
    global sid, creator_id
    device_id = msg.text.strip().lower()
    await msg.answer('Запрос отправлен')
    result = await get_object(device_id)
    if result is not None and 'error' in result:
        await msg.answer(
            'При запросе в Wialon произошла ошибка.{}'.format(json.dumps(result) if result is not None else ''))
        return None
    elif result is not None:
        try:
            address = await get_address(result['pos']['x'], result['pos']['y'])
        except:
            address = '-'
        await msg.answer('Информация по объекту с ID {}\n\nАдрес: {}\n\nОбщая информация: {}'.format(
            device_id,
            address,
            json.dumps(
                result)))
    else:
        result = await create_object(device_id, model_id, msg)
        if result is None:
            return None
        if result is not None and 'error' in result:
            await msg.answer(
                'При запросе в Wialon произошла ошибка. {}'.format(json.dumps(result) if result is not None else ''))
            return None
        else:
            await msg.answer('Началась проверка')
            chat_id = msg.chat.id
            thread = Thread(target=check_message_callback, args=(chat_id, device_id))
            thread.start()
            thread.join()
    return None


def check_message_callback(chat_id, device_id):
    dp.loop.create_task(check_message(chat_id, device_id))


async def get_address(x, y):
    result = '-'
    response2 = requests.get(
        'https://geocode-maps.wialon.com/hst-api.wialon.com/gis_geocode?coords=[{"lon":' + str(x) + ',"lat":' + str(
            y) + '}]&flags=1255211008&uid=' + str(creator_id))
    response2 = response2.json()
    if 'error' in response2:
        result = '-'
    if len(response2) > 0:
        result = response2[0]
    return result


async def check_message(chat_id, device_id):
    global sid, creator_id
    start_ts = calendar.timegm(time.gmtime())
    await asyncio.sleep(300)
    while (calendar.timegm(time.gmtime()) - start_ts) < 900:
        object_info = await get_object(device_id)
        if 'lmsg' in object_info and object_info['lmsg'] is not None:
            try:
                address = await get_address(object_info['pos']['x'], object_info['pos']['y'])
            except:
                address = '-'
            await bot.send_message(chat_id=chat_id,
                                   text='Информация по объекту с ID {}\n\nАдрес: {}\n\nОбщая информация: {}'.format(
                                       device_id,
                                       address,
                                       json.dumps(
                                           object_info)))
            return None
        else:
            await bot.send_message(chat_id=chat_id,
                                   text='Объект с ID {} не на связи, проверьте пожалуйста подключение/настройки'.format(
                                       device_id))
        await asyncio.sleep(300)
    await bot.send_message(chat_id=chat_id,
                           text='С объектом ID {} связаться не удалось'.format(
                               device_id))


async def process_fleetguide_4(msg):
    # 23951816
    await process_device(msg, 23951816)


async def process_fleetguide_6(msg):
    # 23951846
    await process_device(msg, 23951846)


async def ping():
    global sid, creator_id
    while True:
        response = requests.get(
            'https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_items&params={"spec":{"itemsType":"avl_unit","propName":"sys_unique_id","propValueMask":"*ping*","sortType":"sys_name"},"force":1,"flags":1025,"from":0,"to":0}&sid=' + str(
                sid))
        response = response.json()
        await asyncio.sleep(20)


def get_wialon_token_from_file():
    with open('/home/telebot/telegram-bot/wialon_token.txt') as f:
        s = f.read()
    f.close()
    return s


def update_wialon_token():
    global WIALON_TOKEN
    result = requests.post('https://portal.stavtrack.ru/token_wialon/',
                           data={'auth': 'telebot', 'pass': 'stavtrack-26'})
    try:
        WIALON_TOKEN = result.json()['token']
        with open("/home/telebot/telegram-bot/wialon_token.txt", "w") as file:
            file.write(result.json()['token'])
            file.close()
        get_sid()
    except:
        pass


async def async_update_wialon_token():
    global WIALON_TOKEN
    result = requests.post('https://portal.stavtrack.ru/token_wialon/',
                           data={'auth': 'telebot', 'pass': 'stavtrack-26'})
    try:
        WIALON_TOKEN = result.json()['token']
        with open("/home/telebot/telegram-bot/wialon_token.txt", "w") as file:
            file.write(result.json()['token'])
            file.close()
        get_sid()
    except:
        pass


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if len(msg.text) != 6:
        await msg.answer('ID устройства должен состоять из 6 цифр')
        return None
    if msg.text.strip().lower()[0] == '1':
        await process_fleetguide_4(msg)
    elif msg.text.strip().lower()[0] == '9':
        await process_fleetguide_6(msg)
    else:
        await msg.answer('ID устройства должен начинаться на 1 или 9')
        return None


if __name__ == '__main__':
    WIALON_TOKEN = get_wialon_token_from_file()
    get_sid()
    print(sid)
    print(creator_id)
    dp.loop.create_task(ping())
    executor.start_polling(dp, skip_updates=True)
