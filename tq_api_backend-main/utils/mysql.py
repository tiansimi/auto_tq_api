# -*- coding:utf-8 -*-
# @Time   : 2022/2/10 13:21
# @Author : tq
# @File   : mysql.py
import time
import datetime

import pymysql
from utils.log import log


class HandleMysql:
    """ 操作 mysql 数据库的类，创建 mysql 实例, 并提供查询,更新、修改、删除、创建语句等一系列方法 """
    __instance = None

    def __init__(self, db_config, type_data='stream'):
        """ 初始化,指定游标类型,自动提交数量 """

        self.db_config = db_config

        self.type_data = type_data
        self._conn, self._curs = self._get_conn_curs(db_config=self.db_config, type_data=self.type_data)

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        return cls.__instance

    def __del__(self):
        """ 关闭游标和连接 """
        try:
            if self._curs:
                self._curs.close()
        except Exception as e:
            log.error(e)
            raise e
        finally:
            if self._conn:
                self._conn.close()

    def _get_conn(self, dbconfig_dict):
        """ 获取连接 """
        dbconfig_dict['port'] = int(dbconfig_dict['port']) if isinstance(dbconfig_dict['port'], str) else dbconfig_dict[
            'port']
        conn = pymysql.connect(**dbconfig_dict)
        return conn

    def _get_cursor(self, conn, type_data='stream'):
        """ 获取游标 """
        if type_data == 'stream':
            return conn.cursor(pymysql.cursors.SSCursor)  # 返回流式游标,查询大量数据时不占用内存(返回数据形式是元组)
        elif type_data == 'dict':
            return conn.cursor(pymysql.cursors.DictCursor)  # 返回字典形式游标,查询出的数据以字典形式返回
        elif type_data == 'default':
            return conn.cursor()
        else:
            log.error('游标类型错误！')
            raise Exception('游标类型错误！')

    def _get_conn_curs(self, db_config, type_data='stream'):
        """ 获取连接和游标 """
        conn = self._get_conn(db_config)
        curs = self._get_cursor(conn, type_data=type_data)
        return conn, curs

    def is_connected(self, num=2):
        """ 检查服务器是否是活动状态 """
        n = 0
        while True:
            try:
                self._conn.ping(reconnect=True)
                log.info('数据库可以 ping通，是活动状态')
                return True
            except Exception as e:
                n += 1
                log.error(f'重新连接第 {n} 次！')
                self._conn, self._curs = self._get_conn_curs(db_config=self.db_config, type_data=self.type_data)
                if n >= num:
                    log.error(f'数据库连接重新连接 {n} 次后，扔不能连接到数据库\n报错信息：{e}')
                    raise

    def select(self, select_sql):
        """
        查询sql语句返回的所有数据
        :param select_sql: 查询语句
        :return: 查询到的所有数据
        """
        try:
            self._curs.execute(select_sql)
        except pymysql.Error as e:
            log.error(f'SQL有误!select语句：{select_sql}错误内容: {e}')
            raise
        else:
            if self._curs.rowcount == 1:
                log.info(f'select执行成功!select语句:"{select_sql}"结果 1 条数据')
                return self._curs.fetchone()
            else:
                result = self._curs.fetchall()
                log.info(f'select执行成功!select语句:"{select_sql}"结果 {len(result)} 条数据')
                return result

    def update_delete_insert(self, sql):
        """
        执行 更新、删除、插入操作
        :param sql: sql 语句
        :return:
        """
        try:
            self.is_connected()
            self._curs.execute(sql)
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            log.error(f'sql 执行失败,已进行回滚操作!\nsql 语句:"{sql}"\n失败内容为:{e}')
            raise
        else:
            # 判断是否更新成功
            if self._curs.rowcount == 1:
                log.info(f'sql 执行成功!\nsql语句:"{sql}"')
            else:
                log.warning(f'sql 执行成功!\nsql语句:"{sql}"\nwarning:更新后的值与更新之前的值相等，或者查询不到对应的结果')
            return self._curs.rowcount

    def delete(self, delete_sql):
        """ 删除数据 """
        try:
            self.is_connected()
            self._curs.execute(delete_sql)
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            log.error(f'delete执行失败!已进行回滚操作\ndelete语句:"{delete_sql}", 失败内容为:{e}')
            raise
        else:
            # 判断是否删除成功
            if self._curs.rowcount == 1:
                log.info(f'delete执行成功!\ndelete语句:"{delete_sql}"')
            else:
                log.warning(f'delete执行成功!\ndelete语句:"{delete_sql}"\nwarning:删除了0条数据，或者查询不到对应的结果')

    def insert(self, insert_sql):
        """ 插入数据 """
        try:
            self.is_connected()
            self._curs.execute(insert_sql)
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            log.error(f'insert执行失败!已进行回滚操作\ninsert语句:"{insert_sql}", 失败内容为:{e}')
            raise
        else:
            # 判断是否插入成功
            if self._curs.rowcount == 1:
                log.info(f'insert执行成功!\ninsert语句:"{insert_sql}"')
            else:
                log.warning(f'insert执行成功!\ninsert语句:"{insert_sql}"\nwarning:插入了0条数据，或者查询不到对应的结果')

    def select_field(self, select_sql):
        """
        查询数据: 带字段名称和数据
        :param select_sql: 查询语句
        :return: ((字段名称1,字段名称2),[(第1行值1，第1行值2),(第2行值1，第2行值2)])
        """
        try:
            self._curs.execute(select_sql)
            field = [f[0] for f in self._curs.description]
        except Exception as e:
            log.error(f'SQL有误!\nselect语句:"{select_sql}"\n错误内容 {e}')
            raise
        else:
            if self._curs.rowcount == 1:
                log.info(f'select执行成功!\nselect语句:"{select_sql}"\n结果 1 条数据')
                return field, list(self._curs.fetchone())
            else:
                log.info(f'select执行成功!\nselect语句:"{select_sql}"\n结果 n 条数据')
                return field, list(self._curs.fetchall())

    def select_dict(self, select_sql):
        """
        查询数据: 带字段名称和数据
        :param select_sql: 查询语句
        :return: ((字段名称1,字段名称2),[(第1行值1，第1行值2),(第2行值1，第2行值2)])
        """
        try:
            self._curs.execute(select_sql)
        except Exception as e:
            log.error(f'SQL有误!select语句:"{select_sql}"错误内容 {e}')
            raise
        else:
            if self._curs.rowcount == 1:
                ret = self._curs.fetchone()
                for key in ret:
                    if isinstance(ret[key], datetime.datetime):
                        if ret[key].year == 1970:  # 数据库为空会显示“1970-01-01 08:00:00”， timestamp() 读取会报错
                            continue
                        ret[key] = datetime.datetime.timestamp(ret[key])
                result = ret
                log.info(f'select执行成功!select语句:"{select_sql}"结果 1 条数据')
                return result
            else:
                log.info(f'select执行成功!select语句:"{select_sql}"结果 n 条数据')
                return self._curs.fetchall()


if __name__ == '__main__':
    from conf.config import conf
    mysql = HandleMysql(eval(conf.db_info), type_data='dict')
    # sql = "select cast(cast(unix_timestamp(now()) as char) as char);"
    # sql = "select cast(regtm as char) as regtm from clnts;"
    sql = "select * from clnts;"
    res = mysql.select_dict(sql)
    for r in res:
        print(type(res[r]))
        print(type(res[r]) == 'datetime.datetime')
        import datetime
        print(isinstance(res[r], datetime.datetime))
    print(res)
    # sql = "select id from clnts;"
    # res = mysql.select(sql)
    # print(res)