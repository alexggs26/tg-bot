from asyncio import sleep
from calendar import timegm
from time import gmtime
from tg_bot.loader import bot, dp
from tg_bot.app.dbworker import Storage
from tg_bot.app.states import States
from tg_bot.app.api.wialon.get_object_info import wialon_get_object_info
from tg_bot.app.keyboard_builder import build_ok_button


async def check_device_wialon_wrapper(device_id, chat_id, user_id, platform):

    button_kb = build_ok_button()

    response_stavros = wialon_get_object_info(device_id=device_id, account=platform)
    data = {
        'user_id': user_id,
        'device_id': device_id
    }
    query = Storage.query_builder(data['user_id'], data, type='update_device_id')
    db_response = Storage.execute_query(query, type='update_device_id')

    if response_stavros['code'] == 'network_error':
        await bot.send_message(chat_id=chat_id, text=response_stavros['description'], reply_markup=button_kb)
        Storage.set_smt_code(user_id, code='error')
        return None

    if (response_stavros['code'] == 'not_exist') or (response_stavros['code'] == 'platform_error'):
        Storage.set_smt_code(user_id, code='not_exist')
        return None
    
    else:
        if response_stavros['code'] == 'no_signal':
            start_ts = timegm(gmtime())
            message_answer = await bot.send_message(chat_id=chat_id, text='Проверяю подключение...')
            Storage.set_smt_code(user_id, code='no_signal')

            while (timegm(gmtime()) - start_ts) < 900:
                tracker_info = wialon_get_object_info(device_id, platform)

                if tracker_info['code'] != 'send_data':

                        if ((timegm(gmtime()) - start_ts) // 60) > 0:
                            response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                (timegm(gmtime()) - start_ts) // 60} минут {(timegm(gmtime()) - start_ts) % 60} секунд..."""
                            await bot.edit_message_text(chat_id=chat_id, message_id=message_answer.message_id, text=response)

                        elif ((timegm(gmtime()) - start_ts) // 60) == 0:
                            response = f"""Объект найден в системе мониторинга Online.Stavtrack.\n\nУстройство не ответило на команды, проверяю подключение...\nПрошло {
                                timegm(gmtime()) - start_ts} секунд..."""
                            await bot.edit_message_text(chat_id=chat_id, message_id=message_answer.message_id, text=response)

                else:
                    await bot.send_message(chat_id=chat_id, text=tracker_info['description'])
                    Storage.set_smt_code(user_id, code='send_data')
                    break

                await sleep(30)

            tracker_info = wialon_get_object_info(device_id, platform)

            if tracker_info['code'] != 'send_data' or tracker_info['code'] != 'no_signal' or 'error' in tracker_info['code']:
                final_message = f'С объектом {device_id} связаться не удалось. Пожалуйста, проверьте подключение/настройки либо оставьте обращение в тех. поддержку!'
                await bot.send_message(chat_id=chat_id, text=final_message, reply_markup=button_kb)
                Storage.set_smt_code(user_id, code='no_signal')
                return final_message

        elif response_stavros['code'] == 'send_data':
            await bot.send_message(chat_id=chat_id, text=response_stavros['description'], reply_markup=button_kb)
            Storage.set_smt_code(user_id, code='send_data')
            return response_stavros['description']

