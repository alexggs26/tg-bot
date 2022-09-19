from fast_bitrix24 import Bitrix

def comment(task_id, object_info) -> None:
    b = Bitrix(BITRIX_WEBHOOK)
    comment_object = {
        'TASK_ID': task_id,
        'FIELDS': {
            'AUTHOR_ID': 851,
            'POST_MESSAGE': object_info['message']
        }
    }
    method = 'task.commentitem.add'
    response = b.call(method, comment_object)
    except:
        pass
    