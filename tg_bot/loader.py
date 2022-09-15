from aiogram import Bot, Dispatcher

from tg_bot.app.config import TOKEN


# Объект бота
bot = Bot(token=TOKEN)

# Диспетчер для бота
dp = Dispatcher(bot)


