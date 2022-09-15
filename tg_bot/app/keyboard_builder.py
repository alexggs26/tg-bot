from tg_bot.loader import bot, dp
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from tg_bot.app.dbworker import Storage




page_cb = CallbackData("text", "platform", "num")
hw_cb = CallbackData("hw", "id", "platform")



def build_ok_button():
    button_ok = InlineKeyboardButton(text='Готово', callback_data='start')
    button_kb = InlineKeyboardMarkup().add(button_ok)
    return button_kb


def get_device_list(platform):
    query = f"""
        SELECT name, id
        FROM smt_hw_types
        WHERE objects_count > 0
        AND platform = '{platform}'
        ORDER BY objects_count desc
    """
    device_list = Storage.execute_query(query, type='read_many')
    list = []
    for i in device_list:
        list.append({
            'text': i[0],
            'callback_data': i[1]
        })

    return list


list_devices_wialon = get_device_list('wialon')
list_device_wialon_id = []

for i in list_devices_wialon:
    list_device_wialon_id.append(i['callback_data'])


list_devices_navixy = get_device_list('navixy')
list_device_navixy_id = []

for i in list_devices_navixy:
    list_device_navixy_id.append(i['callback_data'])





def get_pagination(current_page, platform):

    keyboard = InlineKeyboardMarkup()

    if platform == 'navixy' or platform == None:
        max_page = 10

        if (current_page == 1) and (current_page < max_page):
            btn1 = InlineKeyboardButton(
                text='-1-', callback_data=page_cb.new(num='1', platform='navixy'))
            btn2 = InlineKeyboardButton(
                text=f'{current_page+1}>>', callback_data=page_cb.new(num=current_page+1, platform='navixy'))
            btn3 = InlineKeyboardButton(
                text=f'{current_page+2}>>', callback_data=page_cb.new(num=current_page+2, platform='navixy'))
            keyboard.row(btn1, btn2, btn3)

        if (current_page < max_page) and (current_page > 1):
            btn1 = InlineKeyboardButton(
                text=f'<<{current_page-1}', callback_data=page_cb.new(num=current_page-1, platform='navixy'))
            btn2 = InlineKeyboardButton(
                text=f'-{current_page}-', callback_data=page_cb.new(num=current_page, platform='navixy'))
            btn3 = InlineKeyboardButton(
                text=f'{current_page+1}>>', callback_data=page_cb.new(num=current_page+1, platform='navixy'))
            keyboard.row(btn1, btn2, btn3)

        if (current_page == max_page) and (current_page > 1):
            btn1 = InlineKeyboardButton(
                text=f'<<{current_page-2}', callback_data=page_cb.new(num=current_page-2, platform='navixy'))
            btn2 = InlineKeyboardButton(
                text=f'-{current_page-1}-', callback_data=page_cb.new(num=current_page-1, platform='navixy'))
            btn3 = InlineKeyboardButton(
                text=f'-{current_page}-', callback_data=page_cb.new(num=current_page, platform='navixy'))
            keyboard.row(btn1, btn2, btn3)

        for i in list_devices_navixy[(current_page*5-5):(current_page*5)]:
            btn = InlineKeyboardButton(
                text=i['text'], callback_data=hw_cb.new(id=i['callback_data'], platform='navixy')
            )
            keyboard.add(btn)

        return keyboard

    else:
        max_page = 12

        if (current_page == 1) and (current_page < max_page):
            btn1 = InlineKeyboardButton(
                text='-1-', callback_data=page_cb.new(num='1', platform='wialon'))
            btn2 = InlineKeyboardButton(
                text=f'{current_page+1}>>', callback_data=page_cb.new(num=current_page+1, platform='wialon'))
            btn3 = InlineKeyboardButton(
                text=f'{current_page+2}>>', callback_data=page_cb.new(num=current_page+2, platform='wialon'))
            keyboard.row(btn1, btn2, btn3)

        if (current_page < max_page) and (current_page > 1):
            btn1 = InlineKeyboardButton(
                text=f'<<{current_page-1}', callback_data=page_cb.new(num=current_page-1, platform='wialon'))
            btn2 = InlineKeyboardButton(
                text=f'-{current_page}-', callback_data=page_cb.new(num=current_page, platform='wialon'))
            btn3 = InlineKeyboardButton(
                text=f'{current_page+1}>>', callback_data=page_cb.new(num=current_page+1, platform='wialon'))
            keyboard.row(btn1, btn2, btn3)

        if (current_page == max_page) and (current_page > 1):
            btn1 = InlineKeyboardButton(
                text=f'<<{current_page-2}', callback_data=page_cb.new(num=current_page-2, platform='wialon'))
            btn2 = InlineKeyboardButton(
                text=f'<<{current_page-1}', callback_data=page_cb.new(num=current_page-1, platform='wialon'))
            btn3 = InlineKeyboardButton(
                text=f'-{current_page}-', callback_data=page_cb.new(num=current_page, platform='wialon'))
            keyboard.row(btn1, btn2, btn3)

        for i in list_devices_wialon[(current_page*5-5):(current_page*5)]:
            btn = InlineKeyboardButton(
                text=i['text'], callback_data=hw_cb.new(id=i['callback_data'], platform='wialon'))
            keyboard.add(btn)
        
        return keyboard
    

async def send_page(chat_id, platform):
    page_keyboard = get_pagination(1, platform)
    await bot.send_message(chat_id=chat_id, text="Доступные типы устройств:", reply_markup=page_keyboard)
    return None


@dp.callback_query_handler(page_cb.filter())
async def update_page(call: CallbackQuery, callback_data: dict):
    page_num = int(callback_data.get('num'))
    platform = callback_data.get('platform')

    if platform == 'navixy':
        page_keyboard = get_pagination(page_num, 'navixy')
        await call.message.edit_reply_markup(reply_markup=page_keyboard)
        return None

    else:
        page_keyboard = get_pagination(page_num, 'wialon')
        await call.message.edit_reply_markup(reply_markup=page_keyboard)
        return None


def register_update_page(dp):
    dp.register_callback_query_handler(update_page, page_cb.filter())
