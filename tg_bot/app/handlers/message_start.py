from tg_bot.loader import bot, dp
from aiogram.types.message import Message 
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from tg_bot.app.dbworker import Storage
from tg_bot.app.states import States
from datetime import datetime


@dp.message_handler(commands="start")
async def show_main_menu(message: Message):

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text='Проверка оборудования',
            callback_data='check_device'
        ),
        # InlineKeyboardButton(
        #     text='Инструкции',
        #     callback_data='instructions'
        # ),
        InlineKeyboardButton(
            text='Заявка в тех. поддержку',
            callback_data='ticket'
        )
    )
    await message.answer(
        text="""С помощью этого бота можно проверить работу телематического оборудования.\n\nДля проверки нужно знать ID (IMEI) устройства, ID учетной записи и определить тип устройства.\nВ течение 15 минут бот отправляет запрос к серверу на получение местоположения.\nЕсли бот заглючит - попробуйте отправить команду /start
    """, reply_markup=keyboard
    )

    data = {
        'user_id': message.from_user.id,
        'user_name': message.from_user.username,
        'chat_id': message.chat.id,
        'state': States.S_START.value,
        'phone': None,
        'device_id': None,
        'hw_id': None,
        'client_sys_id': None,
        'client_platform': None,
        'dt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    current_state = Storage.get_state(message.from_user.id)
    if current_state == None:
        query = Storage.query_builder(data['user_id'], data, type='write')
        response = Storage.execute_query(query, type='write')
        if 'Ошибка' in response:
            await bot.send_message(chat_id=message.chat.id, text=response)
        return None

    else:
        Storage.set_state(message.from_user.id, States.S_START.value)
        return None
    

def register_message_start(dp):
    dp.register_message_handler(show_main_menu, commands="start")