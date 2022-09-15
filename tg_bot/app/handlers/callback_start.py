from tg_bot.loader import dp
from tg_bot.app.dbworker import Storage
from tg_bot.app.states import States
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


@dp.callback_query_handler(text="start")
async def show_main_menu(call: CallbackQuery):
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
    await call.message.answer(
        """С помощью этого бота можно проверить работу телематического оборудования.\n\nДля проверки нужно знать ID (IMEI) устройства, ID учетной записи и определить тип устройства.\nВ течение 15 минут бот отправляет запрос к серверу на получение местоположения.\nЕсли бот заглючит - попробуйте отправить команду /start
    """, reply_markup=keyboard
    )
    Storage.set_state(call.message.from_user.id, States.S_START.value)
    return None


def register_callback_start(dp):
    dp.register_callback_query_handler(show_main_menu, text='start')