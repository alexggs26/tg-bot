from tg_bot.app.config import DB_HOST, DB_USER, DB_PW, DB_DATABASE, DB_TABLE
from pymysql import Error, connect




class Storage():
    """
    класс взаимодействия с БД MySQL
    реализовано 8 методов :
    execute_query для выполнения запроса к БД
    get_token - возвращает актуальный токен
    write_token - записывает новый токен
    update_token - обновляет токен для учетной записи
    get state - возвращает статус по user_id
    set_state - апдейтит статус юзера по user_id
    get_client_id - возвращает значение для определения, куда заносить объект
    get_phone - --//--
    set_phone - --//--
    query_builder для построения запроса
    """

    @staticmethod
    def execute_query(query, type):
        con = connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PW,
            database=DB_DATABASE
        )
        cursor = con.cursor()
        try:
            cursor.execute(query)
        except Error as e:
            result = f'Ошибка базы данных: {e}'
            return result
        else:
            if type == 'read_one':
                result = cursor.fetchone()
                return result
            elif type == 'read_many':
                result = cursor.fetchall()
                return result
            elif type in ('write', 'update', 'update_all', 'update_client_info', 'update_device_id', 'update_phone', 'update_hw_id', 'delete'):
                con.commit()
                result = 'OK'
                return result
        finally:
            cursor.close()
            con.close()


    @staticmethod
    def get_token(account):
        query = f"""
            SELECT token
            FROM marketing.tg_bot_success_token
            WHERE account = '{account}'
        """
        token = Storage.execute_query(query, type='read_one')[0]
        return token


    @staticmethod
    def write_token(token, account):
        query = f"""
            INSERT INTO marketing.tg_bot_success_token
            VALUES ({token}, {account}, current_timestamp())
        """
        Storage.execute_query(query, type='write')
        return None


    @staticmethod
    def update_token(token, account):
        query = f"""
            UPDATE marketing.tg_bot_success_token
            SET token = '{token}'
            WHERE id > 0 AND account = '{account}'
        """
        response = Storage.execute_query(query, type='update')
        return response


    @staticmethod
    def get_state(user_id):
        query = f"""
            SELECT state
            FROM {DB_TABLE}
            WHERE user_id = '{user_id}'
        """
        state = Storage.execute_query(query, type='read_one')
        if state == None:
            return state
        else:
            return state[0]


    @staticmethod
    def set_state(user_id, state):
        query = f"""
            UPDATE {DB_TABLE}
            SET state = '{state}'
            WHERE user_id = '{user_id}'
        """
        Storage.execute_query(query, type='update')
        return None


    @staticmethod
    def get_smt_code(user_id):
        query = f"""
            SELECT smt_code
            FROM {DB_TABLE}
            WHERE user_id = '{user_id}'
        """
        code = Storage.execute_query(query, type='read_one')
        if code == None:
            return code
        else:
            return code[0]


    @staticmethod
    def set_smt_code(user_id, code):
        query = f"""
            UPDATE {DB_TABLE}
            SET smt_code = '{code}'
            WHERE user_id = '{user_id}'
        """
        Storage.execute_query(query, type='update')
        return None
        
    @staticmethod
    def get_client_id(task_id):
        query = f"""
            SELECT crm_client_id, sys_client_id, platform
            FROM marketing.smt_clients
            WHERE crm_client_id like concat(
            (SELECT DISTINCT comp.id
            FROM dbportal.b_crm_company AS comp
            LEFT JOIN dbportal.b_uts_crm_invoice as uti on comp.id = uti.uf_company_id
            LEFT JOIN ( 
                SELECT value_id, substring(value, 3, 6) AS deal_id 
                FROM dbportal.b_utm_tasks_task 
                where value like 'D%') 
                AS deal_t ON uti.uf_deal_id = deal_t.deal_id
            where deal_t.value_id = '{task_id}'), '%')
            
            UNION

            SELECT crm_client_id, sys_client_id, platform
            FROM marketing.smt_clients
                    WHERE crm_client_id like concat(
                    (SELECT DISTINCT comp.id
                    FROM dbportal.b_crm_company AS comp
                    LEFT JOIN ( 
                        SELECT value_id, substring(value, 4, 6) AS comp_id 
                        FROM dbportal.b_utm_tasks_task 
                        where value like 'CO%') 
                        AS comp_t ON comp.id = comp_t.comp_id
                    where comp_t.value_id ='{task_id}'), '%')
        """
        result = Storage.execute_query(query, type='read_one')
        return result


    @staticmethod
    def get_phone(user_id):
        query = f"""
            SELECT phone
            FROM marketing.tg_bot_storage
            where user_id = {user_id}
        """
        result = Storage.execute_query(query, type='read_one')
        if result == None:
            return result
        else:
            return result[0]


    @staticmethod
    def set_phone(user_id, phone):
        query = f"""
            UPDATE marketing.tg_bot_storage
            SET phone = '{phone}'
            WHERE user_id = {user_id}
        """
        Storage.execute_query(query, type='update_phone')
        return None

    @staticmethod
    def get_crm_company_id(task_id):
        query = f"""
            SELECT DISTINCT comp.id
            FROM dbportal.b_crm_company AS comp
            LEFT JOIN dbportal.b_uts_crm_invoice as uti on comp.id = uti.uf_company_id
            LEFT JOIN ( 
                SELECT value_id, substring(value, 3, 6) AS deal_id 
                FROM dbportal.b_utm_tasks_task 
                where value like 'D%') 
                AS deal_t ON uti.uf_deal_id = deal_t.deal_id
            where deal_t.value_id = '{task_id}'

            UNION

            SELECT DISTINCT comp.id
            FROM dbportal.b_crm_company AS comp
            LEFT JOIN ( 
                SELECT value_id, substring(value, 4, 6) AS comp_id 
                FROM dbportal.b_utm_tasks_task 
                where value like 'CO%') 
                AS comp_t ON comp.id = comp_t.comp_id
            where comp_t.value_id ='{task_id}'
        """
        result = Storage.execute_query(query, type='read_one')
        return result

    @staticmethod
    def get_task(user_id):
        query = f"""
            SELECT task_id
            FROM {DB_TABLE}
            WHERE user_id = '{user_id}'
        """
        result = Storage.execute_query(query, type='read_one')
        return result[0]

    @staticmethod
    def set_task(user_id, task_id):
        query = f"""
            UPDATE {DB_TABLE}
            SET task_id = '{task_id}'
            WHERE user_id = '{user_id}'
        """
        Storage.execute_query(query, type='update')
        return None


    @staticmethod
    def query_builder(user_id, data, type):
        if type == 'read':
            query = f"""
                SELECT chat_id, state, phone, device_id, hw_id, client_sys_id, client_platform, task_id
                FROM {DB_TABLE}
                WHERE user_id = {user_id}
            """
            return query

        elif type == 'write':
            query = f"""
                INSERT INTO {DB_TABLE} VALUES (
                    '{data['user_id']}',
                    '{data['user_name']}',
                    '{data['chat_id']}',
                    '{data['state']}',
                    '{data['phone']}',
                    '{data['device_id']}',
                    '{data['hw_id']}',
                    '{data['client_sys_id']}',
                    '{data['client_platform']}',
                    '{data['dt']}')
            """
            return query

        elif type == 'update_all':
            query = f"""
                UPDATE {DB_TABLE}
                SET 
                user_id = '{data['user_id']},
                user_name = '{data['user_name']},
                chat_id = '{data['chat_id']},
                state = '{data['state']},
                phone = '{data['phone']},
                device_id = '{data['device_id']},
                client_sys_id = '{data['client_sys_id']},
                client_platform = '{data['client_platform']}
                WHERE user_id = {user_id}
            """
            return query

        elif type == 'update_device_id':
            query = f"""
                UPDATE {DB_TABLE}
                SET 
                device_id = '{data['device_id']}'
                WHERE user_id = {user_id}
            """
            return query

        elif type == 'update_hw_id':
            query = f"""
                UPDATE {DB_TABLE}
                SET 
                hw_id = '{data['hw_id']}'
                WHERE user_id = {user_id}
            """
            return query

        elif type == 'update_client_info':
            query = f"""
                UPDATE {DB_TABLE}
                SET 
                client_sys_id = '{data['client_sys_id']}',
                client_platform = '{data['client_platform']}'
                WHERE user_id = {user_id}
            """
            return query

        elif type == 'delete':
            query = f"""
                DELETE FROM {DB_TABLE}
                where user_id = '{user_id}'
            """
            return query
