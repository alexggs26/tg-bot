from asyncio import sleep
from calendar import timegm
from time import gmtime
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from tg_bot.loader import bot, dp
from tg_bot.app.dbworker import Storage
from tg_bot.app.states import States
from tg_bot.app.api.navixy.get_object_info import navixy_get_object_info
from tg_bot.app.api.wialon.get_object_info import wialon_get_object_info
from tg_bot.app.keyboard_builder import build_ok_button



@dp.callback_query_handler(text='check_device')
async def process_check_device(call: CallbackQuery):
    
    await call.message.answer(
        text="""
            Введите ID либо IMEI оборудования
            """)  
    Storage.set_state(call.from_user.id, States.S_ENTER_DEVICE_ID.value)
    return None


@dp.message_handler(lambda message: Storage.get_state(message.from_user.id) == States.S_ENTER_DEVICE_ID.value)
async def check_device(message: Message):

    button_kb = build_ok_button()


    if message.text.isdigit() == False:
        await message.answer("""
            ID либо IMEI устройства должен состоять только из цифр
        """)

    else:
        device_id = message.text
        await message.answer('Проверяю объект...')
        response_navixy = await navixy_get_object_info(device_id=device_id)
        data = {
            'user_id': message.from_user.id,
            'device_id': device_id
        }
        query = Storage.query_builder(data['user_id'], data, type='update_device_id')
        db_response = Storage.execute_query(query, type='update_device_id')

        if response_navixy['code'] == 'network_error':
            await bot.send_message(chat_id=message.chat.id, text=response_navixy['description'], reply_markup=button_kb)
            return None

        if (response_navixy['code'] == 'not_exist') or (response_navixy['code'] == 'platform_error'):
            response = 'Объект с таким ID не найден в платформе мониторинга My.Stavtrack. Проверяю другую платформу...'
            await bot.send_message(chat_id=message.chat.id, text=response)
            response_wialon = wialon_get_object_info(device_id, 'stavros')

            if response_wialon['code'] == 'network_error':
                await bot.send_message(chat_id=message.chat.id, text=response_wialon['description'], reply_markup=button_kb)
                return None

            if (response_wialon['code'] == 'not_exist') or (response_wialon['code'] == 'platform_error'):
                response = 'Проверяю платформу Online.Stavtrack...'
                await bot.send_message(chat_id=message.chat.id, text=response)
                response_wialon2 = wialon_get_object_info(device_id, 'stavros2')

                if response_wialon2['code'] == 'network_error':
                    await bot.send_message(chat_id=message.chat.id, text=response_wialon2['description'], reply_markup=button_kb)
                    return None

                if (response_wialon2['code'] == 'not_exist') or (response_wialon2['code'] == 'platform_error'):
                    await bot.send_message(chat_id=message.chat.id,
                        text=f"""Объект с таким ID не найден в платформе мониторинга Online.Stavtrack.\n\nДля создания нового объекта на сервере введите ID Клиента""")
                    Storage.set_state(message.from_user.id, States.S_ENTER_ACCOUNT_ID.value)
                    return None
                    
                else:
                    if response_wialon2['code'] == 'no_signal':
                        start_ts = timegm(gmtime())
                        message_answer = await bot.send_message(chat_id=message.chat.id, text='Проверяю подключение...')
                        
                        tracker_info = wialon_get_object_info(device_id, 'stavros2')
                        if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':

                            while (timegm(gmtime()) - start_ts) < 900:
                                tracker_info = wialon_get_object_info(device_id, 'stavros2')

                                if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':

                                    if ((timegm(gmtime()) - start_ts) // 60) > 0:
                                        response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                        (timegm(gmtime()) - start_ts) // 60} минут {(timegm(gmtime()) - start_ts) % 60} секунд..."""
                                        await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                                    elif ((timegm(gmtime()) - start_ts) // 60) == 0:
                                        response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                            timegm(gmtime()) - start_ts} секунд..."""
                                        await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                                else:
                                    await bot.send_message(chat_id=message.chat.id, text=tracker_info['description'])
                                    break

                                await sleep(30)

                        tracker_info = wialon_get_object_info(device_id, 'stavros2')

                        if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':
                            final_message = f'С объектом {device_id} связаться не удалось. Пожалуйста, проверьте подключение/настройки либо оставьте обращение в тех. поддержку!'
                            await bot.send_message(chat_id=message.chat.id, text=final_message, reply_markup=button_kb)
                            return None
                    
                    elif response_wialon2['code'] == 'send_data':
                        await bot.send_message(chat_id=message.chat.id, text=f'{response_wialon2}', reply_markup=button_kb)
                    return None

            else:
                if response_wialon['code'] == 'no_signal':
                    start_ts = timegm(gmtime())
                    message_answer = await bot.send_message(chat_id=message.chat.id, text='Проверяю подключение...')
                    while (timegm(gmtime()) - start_ts) < 900:
                        tracker_info = wialon_get_object_info(device_id, 'stavros')

                        if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':

                            if ((timegm(gmtime()) - start_ts) // 60) > 0:
                                response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                (timegm(gmtime()) - start_ts) // 60} минут {(timegm(gmtime()) - start_ts) % 60} секунд..."""
                                await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                            elif ((timegm(gmtime()) - start_ts) // 60) == 0:
                                response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                        timegm(gmtime()) - start_ts} секунд..."""
                                await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                            else:
                                await bot.send_message(chat_id=message.chat.id, text=tracker_info['description'])
                                break

                        await sleep(30)

                    tracker_info = wialon_get_object_info(device_id, 'stavros')

                    if 'Ошибка' in tracker_info or 'не найден' in tracker_info or tracker_info['code'] == 'no_signal':
                        final_message = f'С объектом {device_id} связаться не удалось. Пожалуйста, проверьте подключение/настройки либо оставьте обращение в тех. поддержку!'
                        await bot.send_message(chat_id=message.chat.id, text=final_message, reply_markup=button_kb)
                        return None

                elif response_wialon['code'] == 'send_data':
                    await bot.send_message(chat_id=message.chat.id, text=response_wialon['description'], reply_markup=button_kb)
                return None
        else:
            if response_navixy['code'] == 'no_signal':
                start_ts = timegm(gmtime())
                message_answer = await bot.send_message(chat_id=message.chat.id, text='Проверяю подключение...')

                while (timegm(gmtime()) - start_ts) < 900:
                    tracker_info = await navixy_get_object_info(device_id)

                    if 'Ошибка' in tracker_info or tracker_info == None or 'не найден' in tracker_info or 'не выходил на связь' in tracker_info:

                        if ((timegm(gmtime()) - start_ts) // 60) > 0:
                            response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                (timegm(gmtime()) - start_ts) // 60} минут {(timegm(gmtime()) - start_ts) % 60} секунд..."""
                            await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                        elif ((timegm(gmtime()) - start_ts) // 60) == 0:
                            response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                timegm(gmtime()) - start_ts} секунд..."""
                            await bot.edit_message_text(chat_id=message.chat.id, message_id=message_answer.message_id, text=response)

                    else:
                        await bot.send_message(chat_id=message.chat.id, text=tracker_info['description'])
                        break

                    await sleep(30)

                tracker_info = await navixy_get_object_info(device_id)

                if 'Ошибка' in tracker_info or tracker_info == None or 'не найден' in tracker_info or 'не выходил на связь' in tracker_info:
                    final_message = f'С объектом {device_id} связаться не удалось. Пожалуйста, проверьте подключение/настройки либо оставьте обращение в тех. поддержку!'
                    await bot.send_message(chat_id=message.chat.id, text=final_message, reply_markup=button_kb)
                    return None

            elif response_navixy['code'] == 'send_data':
                await bot.send_message(chat_id=message.chat.id, text=response_navixy['description'], reply_markup=button_kb)
            return None


def register_handlers_check_device(dp):
    dp.register_callback_query_handler(process_check_device, text='check_device')
    dp.register_message_handler(check_device, state=States.S_ENTER_DEVICE_ID.value)
