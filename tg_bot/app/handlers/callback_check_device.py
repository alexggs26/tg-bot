from asyncio import sleep
from calendar import timegm
from time import gmtime
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from tg_bot.loader import bot, dp
from tg_bot.app.config import PLATFORMS_WIALON
from tg_bot.app.dbworker import Storage
from tg_bot.app.states import States
from tg_bot.app.functions.check_device_navixy import check_device_navixy_wrapper
from tg_bot.app.functions.check_device_wialon import check_device_wialon_wrapper
from tg_bot.app.keyboard_builder import build_ok_button, build_answer_for_create
from logging import getLogger, basicConfig, INFO


logger = getLogger(__name__)

basicConfig(
    level=INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="errors.log"
)

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

    keyboard_answer_for_create = build_answer_for_create()

    if message.text.isdigit() == False:
        await message.answer("""
            ID либо IMEI устройства должен состоять только из цифр
        """)

    else:

        data = {
        'user_id': message.from_user.id,
        'device_id': message.text
        }
        query = Storage.query_builder(data['user_id'], data, type='update_device_id')
        db_response = Storage.execute_query(query, type='update_device_id')

        await check_device_navixy_wrapper(message.text, message.chat.id, message.from_user.id)
        navixy_code = Storage.get_smt_code(message.from_user.id)
        if navixy_code == 'not_exist':

            code_list = []

            for platform in PLATFORMS_WIALON:
                await check_device_wialon_wrapper(message.text, message.chat.id, message.from_user.id, platform)
                code = Storage.get_smt_code(message.from_user.id)
                code_list.append({platform: code})
                if code == 'send_data':
                    break

            if 'not_exist' in code_list[-1].values():
                message_text = f"Объект с ID {message.text} не найден на платформе мониторинга Stavtrack.\n\nДля проверки устройства необходимо создать новый объект.\n\nСоздать объект?"
                await bot.send_message(chat_id=message.chat.id, text=message_text, reply_markup=keyboard_answer_for_create)
                    


@dp.callback_query_handler(text='create_yes')
async def answer_create_object(call: CallbackQuery) -> None:
    await bot.send_message(chat_id=call.message.chat.id, text='Для создания нового объекта введите номер заказ-наряда по данному Клиенту')
    Storage.set_state(call.from_user.id, States.S_ENTER_ACCOUNT_ID.value)


def register_handlers_check_device(dp):
    dp.register_callback_query_handler(process_check_device, text='check_device')
    dp.register_callback_query_handler(answer_create_object, text='create_yes')
    dp.register_message_handler(check_device, state=States.S_ENTER_DEVICE_ID.value)
