from tg_bot.loader import bot, dp
from asyncio import sleep
from calendar import timegm
from time import gmtime
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from tg_bot.app.dbworker import Storage
from tg_bot.app.states import States
from tg_bot.app.api.navixy.create_navixy_object import create_navixy_object
from tg_bot.app.api.navixy.get_object_info import navixy_get_object_info
from tg_bot.app.api.wialon.create_wialon_object import create_wialon_object_wrapper
from tg_bot.app.api.wialon.get_object_info import wialon_get_object_info
from tg_bot.app.keyboard_builder import build_ok_button, hw_cb



@dp.callback_query_handler(hw_cb.filter())
async def create_object_wialon(call: CallbackQuery, callback_data: dict):
    platform = callback_data.get('platform')
    if platform == 'navixy':
        await call.message.answer(f"""Пожалуйста, введите номер SIM, вставленной в устройство.\nНомер не должен содержать + и других символов
""")
        data = {'hw_id': callback_data.get('id')}
        query = Storage.query_builder(call.from_user.id, data, type='update_hw_id')
        Storage.execute_query(query, type='update_hw_id')
        Storage.set_state(call.from_user.id, States.S_ENTER_PHONE_DEVICE.value)
    else:
        await call.message.answer(text="Создаю объект...")
        hw_id = callback_data.get('id')
        data = {
            'user_id': call.from_user.id
        }
        query = Storage.query_builder(data['user_id'], data, type='read')
        db_response = Storage.execute_query(query, type='read_one')
        device_id = db_response[3]
        client_sys_id = db_response[5]
        client_platform = db_response[6]
        device_name = f"telegram_bot-{device_id}"

        button_kb = build_ok_button()

        if client_platform == 'stavros' or client_platform == 'stavros2':
            query = f"""
                SELECT account_id FROM smt_clients WHERE sys_client_id = {client_sys_id} AND platform = '{client_platform}'
            """
            client_account_id = Storage.execute_query(query, type='read_one')[0]
            response = create_wialon_object_wrapper(
                client_sys_id=client_sys_id,
                client_account_id=client_account_id,
                device_id=device_id, 
                label=device_name,
                model=hw_id, 
                client_platform=client_platform)

            if response['code'] == 1:
                start_ts = timegm(gmtime())
                message_answer = await bot.send_message(chat_id=call.message.chat.id, text='Проверяю подключение...')

                while (timegm(gmtime()) - start_ts) < 900:
                    tracker_info = wialon_get_object_info(device_id, client_platform)

                    if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':

                        if ((timegm(gmtime()) - start_ts) // 60) > 0:
                            response = f"""Устройство не ответило на команды, проверяю подключение...\nПрошло {
                               (timegm(gmtime()) - start_ts) // 60} минут {(timegm(gmtime()) - start_ts) % 60} секунд..."""
                            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_answer.message_id, text=response)

                        elif ((timegm(gmtime()) - start_ts) // 60) == 0:
                            response = f"""Устройство не ответило на команды, проверяю подключение...\nПрошло {
                                timegm(gmtime()) - start_ts} секунд..."""
                            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_answer.message_id, text=response)

                    else:
                        await bot.send_message(chat_id=call.message.chat.id, text=tracker_info)

                    await sleep(30)

                tracker_info = wialon_get_object_info(device_id, client_platform)

                if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':
                    final_message = f'С объектом {device_id} связаться не удалось. Пожалуйста, проверьте подключение/настройки либо оставьте обращение в тех. поддержку!'
                    await bot.send_message(chat_id=call.message.chat.id, text=final_message, reply_markup=button_kb)
                    return None
            
            elif 'Ошибка' in response:
                await bot.send_message(chat_id=call.message.chat.id, text=response, reply_markup=button_kb)
                return None
        

@dp.message_handler(lambda message: Storage.get_state(message.from_user.id) == States.S_ENTER_PHONE_DEVICE.value)
async def create_object_navixy(message: Message):
    if message.text.isdigit() == False:
        await message.answer(
            text='Номер телефона должен содержать только цифры без + и других символов!')

    else:
        phone_device = message.text
        await message.answer(text="Создаю объект...")
        data = {'user_id': message.from_user.id}
        query = Storage.query_builder(data['user_id'], data, type='read')
        db_response = Storage.execute_query(query, type='read_one')

        device_id = db_response[3]
        hw_id = db_response[4]
        client_sys_id = db_response[5]
        device_name = f"telegram_bot-{device_id}"
        button_kb = build_ok_button()

        response = create_navixy_object(
            client_sys_id=client_sys_id,
            device_id=device_id,
            label=device_name,
            model=hw_id,
            phone_device=phone_device)

        if 'создан' in response:
            start_ts = timegm(gmtime())
            message_answer = await bot.send_message(chat_id=message.chat.id, text='Проверяю подключение...')

            while (timegm(gmtime()) - start_ts) < 900:
                tracker_info = await navixy_get_object_info(device_id)

                if 'Ошибка' in tracker_info or tracker_info == None or 'не найден' in tracker_info or 'не выходил на связь' in tracker_info :

                    if ((timegm(gmtime()) - start_ts) // 60) > 0:
                        response = f"""Устройство не ответило на команды, проверяю подключение...\nПрошло {
                            (timegm(gmtime()) - start_ts) // 60} минут {(timegm(gmtime()) - start_ts) % 60} секунд..."""
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                    elif ((timegm(gmtime()) - start_ts) // 60) == 0:
                        response = f"""Устройство не ответило на команды, проверяю подключение...\nПрошло {
                            timegm(gmtime()) - start_ts} секунд..."""
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                else:
                    await bot.send_message(chat_id=message.chat.id, text=tracker_info)

                await sleep(30)

            tracker_info = await navixy_get_object_info(device_id)
            
            if 'Ошибка' in tracker_info or tracker_info == None or 'не найден' in tracker_info or 'не выходил на связь' in tracker_info:
                final_message = f'С объектом {device_id} связаться не удалось. Пожалуйста, проверьте подключение/настройки либо оставьте обращение в тех. поддержку!'
                await bot.send_message(chat_id=message.chat.id, text=final_message, reply_markup=button_kb)
                return None

        elif 'Ошибка' in response:
            await bot.send_message(chat_id=message.chat.id, text=response, reply_markup=button_kb)
            return None


def register_create_object(dp):
    dp.register_callback_query_handler(create_object_wialon, hw_cb.filter())
    dp.register_message_handler(create_object_navixy, state=States.S_ENTER_PHONE_DEVICE.value)
