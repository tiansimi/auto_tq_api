# -*- coding:utf-8 -*-
import json
import sys
import time

import allure

from apis.center_install_uninstall.data_center_install import DataCenterInstall, DataCenterInstallLinux
from utils.file import fo, File
from utils.log import log
from utils.ps_util import Psutil
from utils.regedit_operrate import is_reg_value, get_reg_value
from dictdiffer import diff


class AssertFileRegProcess:
    """ 断言 文件，注册表以及进程 """

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
            with allure.step(f'断言 {img_info}: {len(files)} 个文件是否存在'):
                for file in files:
                    if file not in extend:
                        while True:
                            result = fo.is_exist_path(file)
                            if exist:
                                if result:
                                    log.info(f'断言成功 文件存在，文件为：{file}')
                                    assert result
                                    break
                                else:
                                    time.sleep(0.5)
                                if time.time() > end_time:
                                    log.error(f'断言失败 文件不存在，文件为：{file}')
                                    assert result
                            else:
                                if not result:
                                    log.info(f'断言成功 文件不存在，文件为：{file}')
                                    assert not result
                                    break
                                else:
                                    time.sleep(0.5)
                                if time.time() > end_time:
                                    log.error(f'断言失败 文件存在，文件为：{file}')
                                    assert not result
            if exist:
                log.info(f'断言成功 {img_info}: {len(files)} 个文件或文件夹存在')
            else:
                log.info(f'断言成功 {img_info}: {len(files)} 个文件或文件夹不存在')
        if isinstance(files, str):
            with allure.step(f'断言 {img_info}: 1 个文件存在'):
                if files not in extend:
                    while True:
                        result = fo.is_exist_path(files)
                        if exist:
                            if result:
                                log.info(f'断言成功 文件存在，文件为：{files}')
                                assert result
                                break
                            else:
                                time.sleep(0.5)
                            if time.time() > end_time:
                                log.error(f'断言失败 文件不存在，文件为：{files}')
                                assert result
                        else:
                            if not result:
                                log.info(f'断言成功 文件不存在，文件为：{files}')
                                assert not result
                                break
                            else:
                                time.sleep(0.5)
                            if time.time() > end_time:
                                log.error(f'断言失败 文件存在，文件为：{files}')
                                assert not result
            if exist:
                log.info(f'断言成功 {img_info}: 1 个文件或文件夹存在')
            else:
                log.info(f'断言成功 {img_info}: 1 个文件或文件夹不存在')

    def assert_reg_value(self, img_info, regedits, exist=False, contain=False):
        """
        断言 注册表信息是否正确
        :param img_info:
        :param regedits: 注册表信息列表
        :param exist: value值是否存在
        :param contain: 是否包含
        :return:
        """
        if isinstance(regedits, list):
            for regedit in regedits:
                reg_key, name, value = regedit
                with allure.step(f'断言{img_info}'):
                    val = get_reg_value(reg_key, name)
                    allure.attach(f'{img_info}', f'路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                    if contain:
                        if value in val:
                            log.info(
                                f'断言value包含成功{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{str(val)[:1000]}')
                        else:
                            log.error(
                                f'断言value包含失败{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{str(val)[:1000]}')
                        assert value in val
                    else:
                        if exist:
                            if len(str(val)) > 5:
                                log.info(
                                    f'断言value存在成功{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{str(val)[:1000]}')
                            else:
                                log.error(
                                    f'断言value存在失败{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{str(val)[:1000]}')
                            assert len(str(val)) > 5
                        else:
                            if val == value:
                                log.info(f'断言成功{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                            else:
                                log.error(f'断言失败{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                            assert val == value

        if isinstance(regedits, tuple) and len(regedits) == 3:
            reg_key, name, value = regedits
            with allure.step(f'断言{img_info}'):
                val = get_reg_value(reg_key, name)
                allure.attach(f'{img_info}', f'路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                if contain:
                    if str(val) in val:
                        log.info(f'断言value包含成功{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                    else:
                        log.error(f'断言value包含失败{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                    assert str(val) in val
                else:
                    if exist:
                        if len(str(val)) > 5:
                            log.info(f'断言value存在成功{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                        else:
                            log.error(f'断言value存在失败{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                            assert len(str(val)) > 5
                    else:
                        if val == value:
                            log.info(f'断言成功{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                        else:
                            log.error(f'断言失败{img_info}-路径：{reg_key}，键值名称：{name}，键值数据：期望：{value}，实际：{val}')
                        assert val == value

    def assert_reg_value_not_exist(self, img_info, regedits, extend=[]):
        """
        断言 注册表键值不存在
        :param img_info:
        :param regedits:
        :param extend: 排除验证的键值
        :param contain: 如果存在判断 value 中不包含
        :return:
        """
        if not isinstance(regedits, list):
            raise TypeError('请输入列表形式的数据')
        for regedit in regedits:
            if regedit not in extend:
                reg_key, name, value = regedit
                with allure.step(f'断言 {img_info}'):
                    val = is_reg_value(reg_key, name)
                    allure.attach(f'{img_info}', f'路径：{reg_key}，键值名称：{name}，键值数据：期望：False，实际：{val}')
                    if not val:
                        log.info(f'断言成功-{img_info}。路径：{reg_key}，键值名称：{name}，键值数据：期望：False，实际：{val}')
                        assert not val
                    else:
                        if value not in val:
                            log.info(f'断言成功-{img_info}。路径：{reg_key}，键值名称：{name}，键值数据：期望：不包含{value}，实际：{val}')
                        else:
                            log.error(f'断言失败-{img_info}。路径：{reg_key}，键值名称：{name}，键值数据：期望：False，实际：{val}')
                        assert value not in val

    def assert_process_running(self, img_info, process, not_run=False):
        """ 断言 正在运行的进程 """
        if isinstance(process, str):
            process = [process]
        pro = Psutil().get_process_running(process)
        with allure.step(f'{img_info} - 期望：{process}。实际：{pro}'):
            if not_run:
                if pro == []:
                    log.info(f'断言成功 进程未运行{process}')
                else:
                    log.error(f'断言失败 正在运行的程序：{pro}')
                assert pro == []
            else:
                if pro.sort() == process.sort():
                    log.info(f'断言成功 {len(pro)}个进程正在运行:{pro}')
                else:
                    if isinstance(process, str):
                        log.error(f'断言失败 {len(pro)}个进程正在运行:没有运行的进程为：{process}')
                    else:
                        log.error(f'断言失败 {len(pro)}个进程正在运行:没有运行的进程为：{list(set(process) - set(pro))}')
                assert pro == process

    def wait_process_running(self, img_info, process, timeout=30):
        """ 等待 进程启动 """
        end_time = time.time() + timeout
        if isinstance(process, str):
            process = [process]
        while True:
            time.sleep(3)
            pro = Psutil().get_process_running(process)
            with allure.step(f'{img_info} - 期待：{process}。实际{pro}'):
                if pro.sort() == process.sort():
                    log.info(f'程序启动 {len(pro)}个进程正在运行:{pro}')
                    break
                else:
                    log.info(f'程序{pro}未启动')
                if time.time() > end_time:
                    log.info('超时退出')
                    break

    def assert_process_startup(self, img_info, process, not_run=False):
        """ 断言 自启动中存在进程 """
        if isinstance(process, str):
            process = [process]
        pro = Psutil().get_process_startup(process)
        with allure.step(f'{img_info} - 期望：{process}。实际：{pro}'):
            if not_run:
                if pro == []:
                    log.info(f'断言成功 进程未运行{process}')
                else:
                    log.error(f'断言失败 正在运行的程序：{pro}')
                assert pro == []
            else:
                if pro == process:
                    log.info(f'{len(pro)}个进程在自启动中:{pro}')
                else:
                    if isinstance(process, str):
                        log.error(f'{len(pro)}个进程在自启动中：{process}')
                    else:
                        log.error(f'{len(pro)}个进程在自启动中：{list(set(process) - set(pro))}')
                assert pro == process

    def assert_compare_json_same(self, info, template_file):
        """
        对比两个json文件内容相同
        :param template_file: 模板文件内容
        :return:
        """
        with allure.step(f'{info}'):
            template_file_list = File().get_files(template_file, ['.json'])  # 获取模板文件夹中所有的json文件
            for file in range(0, len(template_file_list)):
                template_files = template_file_list[file]   # 获取第一个json文本
                # 获取对比json文本
                if sys.platform in ('dos', 'win32', 'win16'):
                    file_dirctory = template_file_list[file].split("\\")  # 切割字符串为了获取对比json文本的路径
                    compare_file = f"{DataCenterInstall().data_install_config}\\{file_dirctory[-2]}\\{file_dirctory[-1]}"
                else:
                    file_dirctory = template_file_list[file].split("/")  # 切割字符串为了获取对比json文本的路径
                    compare_file = f"{DataCenterInstallLinux().data_install_config}/{file_dirctory[-2]}/{file_dirctory[-1]}"
                try:
                    with open(template_files, 'r', encoding="utf-8") as fp:
                        template_files_js = json.load(fp)
                    with open(compare_file, 'r', encoding="utf-8") as fp:
                        compare_file_js = json.load(fp)

                    dif = list(diff(template_files_js, compare_file_js))  # 默认模板和本次安装后验证的数字签名进行对比
                    if dif:
                        allure.attach(f'验证{file_dirctory[-2]}文件，期望{template_files}与{compare_file}内容相同，返回[]空列表,实际结果：{dif}')
                        log.info(f'验证{file_dirctory[-2]}文件，期望{template_files}与{compare_file}，返回字段：{dif}')
                    else:
                        allure.attach(f'验证{file_dirctory[-2]}文件，期望{template_files}与{compare_file}内容相同，返回[]空列表,实际结果：{dif}')
                        log.info(f'验证{file_dirctory[-2]}文件，期望{template_files}与{compare_file}，返回字段：{dif}')
                    assert not dif
                except Exception as e:
                    print(f'读取json文件错误：{e}')

    def assert_service_running(self, img_info, service_name, not_run=False):
        """ 断言 正在运行的服务 """
        if isinstance(service_name, str):
            process = [service_name]
        pro = Psutil().get_service_running(service_name)
        with allure.step(f'{img_info} - 期望：{service_name}。实际：{pro}'):
            if not_run:
                if pro == []:
                    log.info(f'断言成功 进程未运行{service_name}')
                else:
                    log.error(f'断言失败 正在运行的程序：{pro}')
                assert pro == []
            else:
                if pro.sort() == service_name.sort():
                    log.info(f'断言成功 {len(pro)}个进程正在运行:{pro}')
                else:
                    if isinstance(service_name, str):
                        log.error(f'断言失败 {len(pro)}个进程正在运行:没有运行的进程为：{service_name}')
                    else:
                        log.error(f'断言失败 {len(pro)}个进程正在运行:没有运行的进程为：{list(set(service_name) - set(pro))}')
                assert pro == service_name

