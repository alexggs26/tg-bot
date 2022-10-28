from fast_bitrix24 import Bitrix
from tg_bot.app.config import BITRIX_WEBHOOK, BITRIX_CHAT_ID
from datetime import datetime, timedelta


def create_ticket(phone, user_name):
    b = Bitrix(BITRIX_WEBHOOK)
    title = 'Проверка через бот проверок'
    text = f"""От пользователя Telegram {user_name
    } поступил запрос в тех поддержку по проверке устройства.\nНомер телефона - {phone}.
    """
    time = datetime.now() + timedelta(minutes=15)
    deadline = time.strftime("%Y-%m-%d %H.%M.%S")
    params = {
        'fields': {
            'TITLE': title,
            'DESCRIPTION': text,
            'GROUP_ID': 'group_id',
            'RESPONSIBLE_ID': 'responsible_id',
            'DEADLINE': deadline
        }
    }
    method = 'tasks.task.add'
    response = b.call(method, params)
    task_id = response['task']['id']
    method_send_message = 'im.message.add'
    text_message = f"""
        Новый тикет через бот проверок:\n BASE_URL/{task_id}/
    """
    params_send_message = {
        'DIALOG_ID': BITRIX_CHAT_ID,
        'MESSAGE': text_message
    }
    final_response = b.call(method_send_message, params_send_message)
    return final_response
