from fast_bitrix24 import Bitrix
from tg_bot.app.config import BITRIX_WEBHOOK

def comment(task_id, object_info) -> None:
    print(object_info)
    if object_info == None:
        pass
    else:
        b = Bitrix(BITRIX_WEBHOOK)
        comment_object = {
            'TASK_ID': task_id,
            'FIELDS': {
                'AUTHOR_ID': 'author_id',
                'POST_MESSAGE': f'Результат проверки через бот проверок: \n\n{object_info}'
            }
        }
        method = 'task.commentitem.add'
        response = b.call(method, comment_object)
