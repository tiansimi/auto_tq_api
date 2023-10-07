import allure

from conf.config import Config
from utils.log import log
from utils.mysql import HandleMysql


class ExecuteSql:
    def __init__(self):
        self.conf = Config()

    def select_hress(self, sql, type_data='stream', empty=False):
        """ 执行查询操作
        :param sql: update、delete、insert sql 语句，
        :param type_data: stream:返回流式游标,查询大量数据时不占用内存(返回数据形式是元组)  dict:返回字典形式游标,查询出的数据以字典形式返回
        :param empty：查询结果是否可为空
        """
        mysql = HandleMysql(self.conf.db_info_hress, type_data=type_data)
        result = mysql.select_dict(sql)
        log.info(f'select语句查询结果：{result}')
        if not empty and len(result) == 0:
            raise ValueError(f'查询数据库表结果条数为0！')
        return result

    def update_delete_insert_hress(self, sql, type_data='stream'):
        """ 执行编辑、删除、添加操作
        :param sql: update、delete、insert sql 语句
        :param type_data: stream:返回流式游标,查询大量数据时不占用内存(返回数据形式是元组)  dict:返回字典形式游标,查询出的数据以字典形式返回
        """
        mysql = HandleMysql(self.conf.db_info_hress, type_data=type_data)
        result = mysql.update_delete_insert(sql)
        return result

    def assert_update_delete_insert_hress(self, info, sql, expect=0, type_data='stream'):
        """
        执行编辑、删除、添加操作
        :param info: 步骤信息
        :param sql: update、delete、insert sql 语句
        :param expect: 预期返回条数，默认为 0
        :param type_data: stream:返回流式游标,查询大量数据时不占用内存(返回数据形式是元组)  dict:返回字典形式游标,查询出的数据以字典形式返回
        """
        result = self.update_delete_insert_hress(sql, type_data)

        with allure.step(f'{info}'):
            allure.attach(f'断言 {info}', f'期望结果：{expect}, 实际结果：{result}')
            if result >= expect:
                log.info(f'断言成功 {info}，实际结果大于或等于期望结果: 期望结果：{expect}, 实际结果：{result}')
            else:
                log.error(f'断言失败 {info}，实际结果小于期望结果： 期望结果：{expect}, 实际结果：{result}')
            assert result >= expect
