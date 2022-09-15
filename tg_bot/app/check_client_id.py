from tg_bot.loader import bot, dp
from aiogram.types.message import Message
from tg_bot.app.states import States
from tg_bot.app.dbworker import Storage
from tg_bot.app.keyboard_builder import send_page
from tg_bot.app.api.navixy.create_navixy_user import create_user
# from tg_bot.app.handlers.message_run_scheduler import run_scheduler


@dp.message_handler(lambda message: Storage.get_state(message.from_user.id) == States.S_ENTER_ACCOUNT_ID.value)
async def check_client_id(message: Message):

    task_id = message.text
    await message.answer('Проверяю заказ-наряд...')
    await run_scheduler()
    result = Storage.get_client_id(task_id)

    if result == None:
        await bot.send_message(chat_id=message.chat.id, text='Клиент по данному заказ-наряду не найден в системе мониторинга. Создаю учетную запись...')
        client_sys_id = create_user(result[0])
        await send_page(message.chat.id, 'navixy')
        message_client_sys_id = client_sys_id
        message_platform = 'navixy'

        if type(message_client_sys_id) != int:
            await bot.send_message(chat_id=message.chat.id, text=message_client_sys_id)
            return None

        else:
            data = {
                'user_id': message.from_user.id,
                'client_sys_id': message_client_sys_id,
                'client_platform': message_platform
            }
            query = Storage.query_builder(data['user_id'], data, type='update_client_info')
            response = Storage.execute_query(query, type='update_client_info')
            await run_scheduler()
            return None

    elif result[2] == 'navixy':
        await bot.send_message(
            chat_id=message.chat.id,
            text="""
                Клиент по данному заказ-наряду найден в системе мониторинга My.Stavtrack!\nДля занесения объекта на сервер выберите тип устройства
            """)
        await send_page(message.chat.id, 'navixy')
        client_sys_id = result[1]
        client_platform = 'navixy'
        data = {
            'user_id': message.from_user.id,
            'client_sys_id': client_sys_id,
            'client_platform': client_platform
        }
        query = Storage.query_builder(data['user_id'], data, type='update_client_info')
        response = Storage.execute_query(query, type='update_client_info')
        return None

    elif (result[2] == 'stavros' or result[2] == 'stavros2'):
        await bot.send_message(
            chat_id=message.chat.id,
            text="""
                Клиент по данному заказ-наряду найден в системе мониторинга Online.Stavtrack!\nДля занесения объекта на сервер выберите тип устройства
            """)
        await send_page(message.chat.id, 'wialon')
        client_sys_id = result[1]
        client_platform = result[2]
        data = {
            'user_id': message.from_user.id,
            'client_sys_id': client_sys_id,
            'client_platform': client_platform
        }
        query = Storage.query_builder(data['user_id'], data, type='update_client_info')
        Storage.execute_query(query, type='update_client_info')
        return None


def register_check_client_id(dp):
    dp.register_message_handler(check_client_id, state=States.S_ENTER_ACCOUNT_ID.value)

