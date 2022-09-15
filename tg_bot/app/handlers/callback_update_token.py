from tg_bot.loader import bot, dp
from tg_bot.app.dbworker import Storage
from tg_bot.app.api.wialon.update_token import update_token
from tg_bot.app.keyboard_builder import build_ok_button
from aiogram.types.message import Message



@dp.message_handler(commands='update_token')
async def call_update_token(message: Message):
    result = update_token()
    if result == 'ok':
        kb = build_ok_button()
        await bot.send_message(chat_id=message.chat.id, text="Токен успешно обновлен!", reply_markup=kb)
    

def register_update_token(dp):
    dp.register_message_handler(call_update_token, commands='update_token')
