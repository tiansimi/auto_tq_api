# -*- coding:utf-8 -*-
# @Time   : 2022/2/10 18:44
# @Author : tq
# @File   : assert_api.py
import json
import time

import allure
from jsonpath import jsonpath
from conf.config import conf
from conf.confpath import ConfPath
from utils.file import fo
from utils.log import log
from utils.mysql import HandleMysql
from utils.functions import json_read
from dictdiffer import diff


class AssertApi:
    def __init__(self):
        pass

    def assert_key_exist(self, info, resp, key, exist=True):
        """
        断言 resp 中存在 key 值
        :param info: 描述信息。如：断言key：ts 存在
        :param resp: 字典或json响应数据
        :param key: 期望 存在的键值
        :param exist: 默认断言存在
        :return:
        """
        if isinstance(resp, dict):
            js = jsonpath(resp, f'$..{key}')
            if exist:
                with allure.step(f'{info}-key值-"{key}"存在'):
                    if js is False:
                        allure.attach(f'{info}', f'预期：key值-"{key}"存在；实际：key值-"{key}"不存在；校验值:{resp}')
                        log.error(f'{info}-断言失败-key值-{key}不存在: 返回值:{resp}')
                        assert False
                    else:
                        allure.attach(f'{info}', f'预期："key值-{key}"存在；实际：key值-"{key}"存在；校验值:{resp}')
                        log.info(f'{info}-断言成功-key值-{key}存在, 校验值:{resp}')
                        assert True
            else:
                with allure.step(f'{info}-"{key}"不存在'):
                    if js is False:
                        allure.attach(f'{info}', f'预期："{key}"不存在；实际："{key}"不存在；校验值:{resp}')
                        log.info(f'{info}-断言成功-{key}不存在: 返回值:{resp}')
                        assert True
                    else:
                        allure.attach(f'{info}', f'预期："{key}"不存在；实际："{key}"存在；校验值:{resp}')
                        log.error(f'{info}断言失败-{key}存在, 校验值:{resp}')
                        assert False
        else:
            raise ValueError('断言的resp必须是字典格式！')

    def assert_key_value(self, info, resp, jspath, value, soft_key=None, transition=None, gt=False):
        """ 适用于 获取单个响应字段进行断言
        断言 resp 中 单个字段值 等于 value
        :param info: 描述信息。如：断言key：ts == 176000273
        :param resp: 字典或json响应数据
        :param jspath: jsonpath 表达式 获取单个字段值
        :param value: 期望的 value 值
        :param soft_key: 排序字段
        :param transition：jsonpath()后结果是否需要转换（读取数据库的json字段结果为str格式）
        :param gt 验证大于指定长度
        :return:
        """
        if isinstance(resp, dict):
            js = jsonpath(resp, jspath)
            with allure.step(f'{info}-"{jspath}":"{value}"'):
                if js is not False:
                    allure.attach(f'断言"{jspath}":"{value}"', f'期望：{value}；实际：{js[0]}；校验值:{resp}')
                    if soft_key:
                        if soft_key == 'key':
                            js[0] = sorted(js[0].items(), key=lambda d: d[0])
                        else:
                            if isinstance(js[0][0], dict):
                                js[0] = sorted(js[0], reverse=False, key=lambda key: key[soft_key])
                            elif isinstance(js[0][0], str):
                                js[0] = sorted(js[0])
                    if transition and isinstance(js[0], str):
                        js[0] = json.loads(js[0])   # str转换为dict格式
                    if gt:
                        if js[0] >= value:
                            log.info(f'{info}-断言成功-期望：{value} - 实际：{js[0]}')
                        else:
                            log.error(f'{info}-断言失败-期望：{value} - 实际：{js[0]}')
                        assert js[0] >= value
                    else:
                        if js[0] == value:
                            log.info(f'{info}-断言成功-期望：{value} - 实际：{js[0]}')
                        else:
                            log.error(f'{info}-断言失败-期望：{value} - 实际：{js[0]}')
                        assert js[0] == value
                else:
                    allure.attach(f'{jspath}不存在', f'期望：{value}；实际：{jspath}不存在；校验值:{resp}')
                    log.error(f'断言失败-{jspath}不存在')
                    assert False
        else:
            raise ValueError('断言的resp必须是字典格式！')

    def assert_not_key_value(self, info, resp, jspath):
        """ 断言不存在
        断言 resp 中 单个字段值不存在
        :param info: 描述信息。如：断言key：ts == 176000273
        :param resp: 字典或json响应数据
        :param jspath: jsonpath 表达式 获取单个不存在的字段值
        :return:
        """
        if isinstance(resp, dict):
            js = jsonpath(resp, jspath)
            with allure.step(f'{info}-"{jspath}"'):
                if js is not False:
                    allure.attach(f'断言"{jspath}":不存在', f'期望：{jspath}不存在；实际：{js[0]}；校验值:{resp}')
                    log.error(f'{info}-断言失败-期望：{jspath}不存在 - 实际：{js[0]}；；校验值:{resp}')
                    assert False
                else:
                    allure.attach(f'{jspath}不存在', f'期望：{jspath}不存在；实际：{jspath}不存在；校验值:{resp}')
                    log.info(f'{info}-断言成功-{jspath}不存在；校验值:{resp}')
                    assert not False
        else:
            raise ValueError('断言的resp必须是字典格式！')

    def assert_keys_values(self, info, resp, obj, list_path=None, soft_key=None, **kwargs):
        """ 适用与 多个单个唯一字段进行断言
        断言 resp 中 多个key、value值
        :param info: 描述信息
        :param resp: 字典或json响应数据
        :param obj: 字典对象 {"key1": "value1", "key2", "value2"}
        :param list_path: 先定位到 list  如 $..list[0]
        :param soft_key: 排序字段
        :return:
        """
        if isinstance(resp, dict):
            if kwargs:
                for key, value in kwargs.items():
                    if key in obj:
                        if value == 'exclude':
                            obj.pop(key)

            for key, value in obj.items():
                jspath = f'{list_path}..{key}' if list_path else f'$..{key}'
                js = jsonpath(resp, jspath)
                with allure.step(f'{info}-"{key}":"{value}"'):
                    if js is not False:
                        if soft_key:
                            if isinstance(js[0][0], dict):
                                js[0] = sorted(js[0], reverse=False, key=lambda key: key[soft_key])
                            elif isinstance(js[0][0], str):
                                js[0] = sorted(js[0])
                        if js[0] == value:
                            allure.attach(f'断言"{key}":"{value}"', f'jsonpath:【{jspath}】-期望：{value}；实际：{js}；校验值:{resp}')
                            log.info(f'{info}-断言成功jsonpath: 【{jspath}】-期望：{value} - 实际：{js}；校验值:{resp}')
                        else:
                            allure.attach(f'断言"{key}":"{value}"', f'jsonpath:【{jspath}】-期望：{value}；实际：{js}；校验值:{resp}')
                            log.error(f'{info}-断言失败jsonpath:【{jspath}】-期望：{value} - 实际：{js}；校验值:{resp}')
                        assert js[0] == value
                    else:
                        allure.attach(f'{key}不存在', f'jsonpath: 【{jspath}】期望：{value}；实际：{key}不存在；校验值:{resp}')
                        log.error(f'断言失败jsonpath: 【{jspath}】-{key}不存在；校验值:{resp}')
                        assert False
        else:
            raise ValueError('断言的resp必须是字典格式！')

    def assert_in(self, info, data, ele):
        """
        断言 data 包含 ele
        :param info: 描述信息
        :param data: 数据
        :param ele: 元素
        :return:
        """
        with allure.step(f'{info}-包含："{ele}"'):
            if ele in data:
                allure.attach('断言包含成功', f'期望：包含：{ele}；实际：包含：{ele}；校验值：{data}; ')
                log.info(f'断言包含成功-包含元素：{ele}；校验值：{data}')
            else:
                allure.attach('断言包含失败', f'期望：包含：{ele}；实际：未包含：{ele}；校验值：{data}; ')
                log.error(f'断言包含失败-包含元素：{ele}；校验值：{data}')
            assert ele in data

    def assert_equal(self, info, a, b):
        """
        断言 a == b
        :param info: 描述信息
        :param a:
        :param b:
        :return:
        """
        with allure.step(f'{info}-{a} == {b}'):
            if a == b:
                allure.attach(f'断言 {info} 相等成功', f'期望：{a} == {b}；实际：{a} == {b}')
                log.info(f'断言 {info} 相等成功，期望：{a} == {b}；实际：{a} == {b}')
            else:
                allure.attach(f'断言 {info} 相等失败', f'期望：{a} == {b}；实际：{a} != {b}')
                log.error(f'断言 {info} 相等失败，期望：{a} == {b}；实际：{a} != {b}')
            assert a == b

    def assert_not_equal(self, info, a, b):
        """
        断言 a != b
        :param info: 描述信息
        :param a:
        :param b:
        :return:
        """
        with allure.step(f'{info}-{a} != {b}'):
            if a != b:
                allure.attach('断言不相等成功', f'期望：{a} != {b}；实际：{a} != {b}')
                log.info(f'断言不相等成功，期望：{a} != {b}；实际：{a} != {b}')
            else:
                allure.attach('断言不相等失败', f'期望：{a} != {b}；实际：{a} == {b}')
                log.error(f'断言不相等失败，期望：{a} == {b}；实际：{a} != {b}')
            assert a != b

    def assert_resp_db(self, info, resp, jspath, sql, **kwargs):
        """
        断言响应与mysql数据对比. 支持两种方式 1. 获取返回单个字段 和数据库单个字段对比；2.获取一个字典 和数据库多个字段对比
        :param info:
        :param resp:
        :param jspath: jsonpath 表达式 获取单个字段 或字典
        :param sql: sql语句
        :param kwargs: 修改返回值
                key='int'：把对应值修改为int类型，key='str'：把对应值修改为str类型，key='exclude'：把对应值删除掉不对比
        :return:
        """
        # 实际结果
        db_password = json_read('$..database.password', ConfPath.PATH_SYSCONF)
        db_info = {'host': conf.url_ip, 'port': 3306, 'user': 'root', 'password': db_password, 'database': 'hress'}
        log.info(f'数据库信息：{db_info}')
        result = jsonpath(resp, jspath)
        log.info(f'返回结果jspath：{result}')
        if result is not False:
            result = result[0]
            if kwargs:
                for key, value in kwargs.items():
                    if result[key]:
                        if value == 'int':
                            result[key] = int(result[key])
                        elif value == 'str':
                            result[key] = str(result[key])
                        elif value == 'exclude':
                            result.pop(key)
                        else:
                            result[key] = value
        else:
            raise ValueError(f'jsonpath未能获取到数据：jsonpath表达式：{jspath};响应：{resp}')

        with allure.step('断言响应数据字段 与 查询数据库 一致'):
            if isinstance(result, dict):
                mysql_dict = HandleMysql(db_info, type_data='dict')
                # 期望结果
                result_db = mysql_dict.select_dict(sql)
                log.info(f'数据库结果：{result_db}')
                allure.attach('断言', f'{info} - 期望结果{sql}：{result_db}, 实际结果{jspath}：{str(result)}')

                # 获取两个字典相同的key
                diff = result_db.keys() & result
                # 获取相同key，不同value
                diff_vals = [(k, result_db[k], result[k]) for k in diff if result_db[k] != result[k]]
                if diff_vals:
                    log.error(f'不一致字段：{diff_vals}')
                log.info(f'期望结果：为[]空列表, 实际结果：{diff_vals}')
                assert not diff_vals
            else:
                mysql = HandleMysql(db_info)
                # 期望结果
                result_db = mysql.select(sql)
                log.info(f'{info} - 期望结果{sql}：{str(result_db[0][0])}, 实际结果{jspath}：{str(result)}')
                allure.attach('断言', f'{info} - 期望结果{sql}：{result_db[0][0]}, 实际结果{jspath}：{str(result)}')
                assert result == result_db[0][0]

    def assert_comparison_value(self, info, resp, obj, list_path=None):
        """
        断言两个传入的json的值是否相同
        :param info: 描述信息
        :param resp: 接口返回数据
        :param obj: 验证数据
        :param list_path: json表达式用于从resp中获取指定内容
        :return:
        """
        if isinstance(resp, dict):
            js = jsonpath(resp, list_path)[0]
            dif = list(diff(js, obj))
            with allure.step(f'{info}-"{js}"与"{obj}""的数据相同"'):
                if dif:
                    allure.attach(f'{info} - 期望结果：终端配置与中心配置一致，返回[]空列表, 实际结果：{dif}')
                    log.error(f'{info}，不一致字段：{dif}')
                else:
                    allure.attach(f'{info} - 期望结果：为[]空列表, 实际结果：{dif}')
                    log.info(f'{info} - 期望结果：终端配置与中心配置一致，返回[]空列表, 实际结果：{dif}')
                assert not dif
        else:
            raise ValueError('断言的resp必须是字典格式！')

    def assert_files_exist(self, img_info, files, exist=True, extend=[], timeout=5):
        """
        断言 一个或多个 文件或目录存在
        :param img_info:
        :param files:
        :param exist: False 断言文件或目录不存在
        :param extend: 排除判断的文件或文件夹
        :param timeout 超时时间
        :return:
        """
        end_time = time.time() + timeout
        if isinstance(files, (tuple, list)):
            with allure.step('断言 {}: {} 个文件是否存在'.format(img_info, len(files))):
                for file in files:
                    if file not in extend:
                        while True:
                            result = fo.is_exist_path(file)
                            if exist:
                                if result:
                                    log.info('断言成功 文件存在，文件为：{}'.format(file))
                                    assert result
                                    break
                                else:
                                    time.sleep(0.5)
                                if time.time() > end_time:
                                    log.error('断言失败 文件不存在，文件为：{}'.format(file))
                                    assert result
                            else:
                                if not result:
                                    log.info('断言成功 文件不存在，文件为：{}'.format(file))
                                    assert not result
                                    break
                                else:
                                    time.sleep(0.5)
                                if time.time() > end_time:
                                    log.error('断言失败 文件存在，文件为：{}'.format(file))
                                    assert not result
            if exist:
                log.info('断言成功 {}: {} 个文件或文件夹存在'.format(img_info, len(files)))
            else:
                log.info('断言成功 {}: {} 个文件或文件夹不存在'.format(img_info, len(files)))
        if isinstance(files, str):
            with allure.step('断言 {}: 1 个文件存在'.format(img_info)):
                if files not in extend:
                    while True:
                        result = fo.is_exist_path(files)
                        if exist:
                            if result:
                                log.info('断言成功 文件存在，文件为：{}'.format(files))
                                assert result
                                break
                            else:
                                time.sleep(0.5)
                            if time.time() > end_time:
                                log.error('断言失败 文件不存在，文件为：{}'.format(files))
                                assert result
                        else:
                            if not result:
                                log.info('断言成功 文件不存在，文件为：{}'.format(files))
                                assert not result
                                break
                            else:
                                time.sleep(0.5)
                            if time.time() > end_time:
                                log.error('断言失败 文件存在，文件为：{}'.format(files))
                                assert not result
            if exist:
                log.info('断言成功 {}: 1 个文件或文件夹存在'.format(img_info))
            else:
                log.info('断言成功 {}: 1 个文件或文件夹不存在'.format(img_info))