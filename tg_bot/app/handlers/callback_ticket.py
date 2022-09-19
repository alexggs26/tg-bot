from tg_bot.loader import bot, dp
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from tg_bot.app.dbworker import Storage
from tg_bot.app.api.bitrix.create_ticket import create_ticket
from tg_bot.app.keyboard_builder import build_ok_button
from nest_asyncio import apply as nest_asyncio_apply



@dp.callback_query_handler(text='ticket')
async def build_ticket(call: CallbackQuery):

    phone = Storage.get_phone(call.from_user.id)
    if phone == None:
        kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        button_phone = KeyboardButton(text='Отправить номер телефона', request_contact=True)
        kb.add(button_phone)

        await call.message.answer(text="""Пожалуйста, отправьте свой номер телефона для оставления заявки в тех. поддержку.\nВ течение 15 минут с Вами свяжется дежурный специалист технической поддержки.\nГрафик работы ТП: Пн-Пт с 7:00 до 19:00, Сб-Вс с 8:30 до 17:30""", reply_markup=kb)

    else:
        await bot.send_message(chat_id=call.message.chat.id, text='Запрос в тех. поддержку отправлен! Ищу свободных специалистов')
        nest_asyncio_apply()
        create_ticket(phone, call.from_user.username)


@dp.message_handler(content_types=['contact'])
async def process_ticket(message: Message):
    phone = message.contact.phone_number
    print(phone)
    Storage.set_phone(message.from_user.id, phone)
    await bot.send_message(
        chat_id=message.chat.id, 
        text='Запрос в тех. поддержку отправлен! Ищу свободных специалистов', 
        reply_markup=build_ok_button()
    )
    nest_asyncio_apply()
    create_ticket(phone, message.from_user.username)


def register_callback_ticket(dp):
    dp.register_callback_query_handler(build_ticket, text='ticket')


def register_message_contact(dp):
    dp.register_message_handler(process_ticket, content_types=['contact'])
