from aiogram import executor
from logging import getLogger, basicConfig, INFO
from tg_bot.loader import dp
from tg_bot.app.handlers.message_start import register_message_start
from tg_bot.app.handlers.callback_start import register_callback_start
from tg_bot.app.handlers.callback_check_device import register_handlers_check_device
from tg_bot.app.handlers.callback_create_object import register_create_object
from tg_bot.app.handlers.callback_ticket import register_callback_ticket, register_message_contact
from tg_bot.app.handlers.callback_update_token import register_update_token
from tg_bot.app.keyboard_builder import register_update_page

from tg_bot.app.check_client_id import register_check_client_id



logger = getLogger(__name__)

basicConfig(
    level=INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="bot.log"
)
logger.error("Starting bot")


if __name__ == "__main__":
    executor.start_polling(dp)
