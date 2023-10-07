# -*- coding:utf-8 -*-
# @Time   : 2022/6/30 18:13
# @Author : tq
# @File   : main2.py
from conf.config import Config
from conf.confpath import ConfPath
from utils.report import Report


def run():
    """ 用例运行主入口 pytest 运行参数 """
    args = ['-k', 'hr_high_center_upgrade', '--alluredir', ConfPath.RESULT_LOC_DIR, '--clean-alluredir']
    # args= ['./cases/install_after/hr04_asset_management.py', './cases/install_after/hr05_multistage_center.py', '--alluredir', ConfPath.RESULT_LOC_DIR,
    #        '--clean-alluredir']
    Report().run(args, send=False)  # 发送测试报告


if __name__ == '__main__':
    run()