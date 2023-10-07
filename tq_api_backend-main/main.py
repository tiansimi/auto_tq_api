# -*- coding:utf-8 -*-
# @Time   : 2021/11/19 14:17
# @Author : tq
# @File   : main.py
"""
python main.py 1  # 执行安装测试全部用例
python main.py # 不执行安装测试全部用例
python main2.py # 不执行安装测试单独用例
"""
import os
from conf.config import conf
from conf.confpath import ConfPath
from utils.report import Report
from utils.functions import json_read
from utils.log import log


def run():
    """ 用例运行主入口 pytest 运行参数 """

    branch = json_read('branch', ConfPath.REMOTE_CONFIG_FILE).strip()
    case = json_read('case', ConfPath.REMOTE_CONFIG_FILE).strip()
    if case and branch == 'dev':
        args = ['-k', case, '--alluredir', ConfPath.RESULT_LOC_DIR, '--clean-alluredir']
        Report().run(args, send=True)  # 发送测试报告
    else:
        level_list = []
        level_critical = json_read('level_critical', ConfPath.REMOTE_CONFIG_FILE).strip()
        level_normal = json_read('level_normal', ConfPath.REMOTE_CONFIG_FILE).strip()
        level_minor = json_read('level_minor', ConfPath.REMOTE_CONFIG_FILE).strip()
        if level_critical == '1': level_list.append('critical')
        if level_normal == '1': level_list.append('normal')
        if level_minor == '1': level_list.append('minor')
        level = '--allure-severities=' + ','.join(level_list)
        log.info(f'{level}')
        if level:
            args = ['-k', '{}'.format(conf.modules_case), '--alluredir', ConfPath.RESULT_LOC_DIR, level, '--clean-alluredir']
            if not conf.is_ide:  # 不是ide执行（不加参数）
                Report().run(args, send=True)  # 发送测试报告
            else:
                Report().run(args, send=False)
        else:
            raise ValueError('用例级别最少要选择一个！')
        # os.system("shutdown -s -t 5")  # 运行完关闭系统


if __name__ == '__main__':
    run()
