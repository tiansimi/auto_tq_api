# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 16:34
# @Author : tq
# @File   : conftest.py
import os
import sys
import time
import json

import allure
import pytest
import requests
from conf.confpath import ConfPath
from utils.cmd_line import CmdLine
from utils.file import fo
from utils.log import log
from utils.robot import send_info, create_snapshot
from utils.base_api import BaseApi
from path.page_install import PageInstall
from conf.config import conf

inst = PageInstall()
api = BaseApi()


def pytest_runtest_protocol(item, nextitem):
    """ 每个测试用例执行前，执行一次 """
    log.info(f'---执行开始---：{item.nodeid}')
    send_info(f'-执行开始-{item.nodeid.split("/")[-1]}')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """ 获取用例执行结果的钩子函数（每个测试用例执行完成后，执行一次）  # 用例失败后自动截图 """
    outcome = yield
    report = outcome.get_result()
    filepath = os.path.join(ConfPath.PATH_DIR, 'failures.png')
    if report.when == 'call':
        log.info('---执行结束---：{}'.format(report.nodeid))
    if report.when == 'call' and report.failed:
        branch = fo.json_read('branch', ConfPath.REMOTE_CONFIG_FILE).strip()
        if branch:  # if branch == 'main':
            snapshot_name = item.nodeid.split('::')[-1]
            create_snapshot(snapshot_name.split('[')[0])
            time.sleep(1)

        mode = 'a' if os.path.exists(ConfPath.REPORT_DIR + '/failures') else 'w'
        with open(ConfPath.REPORT_DIR + '/failures', mode) as f:
            if 'tmpir' in item.fixturenames:
                extra = ' (%s) ' % item.funcargs['tmpdir']
            else:
                extra = ''
                f.write(report.nodeid + extra + '\n')
            with allure.step('用例运行失败截图...'):
                if not os.path.exists(filepath):
                    return
                with open(filepath, 'rb') as f:
                    file = f.read()
                    allure.attach(file, '失败截图', allure.attachment_type.PNG)
                    # allure.attach(_driver.get_screenshot_as_png(), '失败截图', allure.attachment_type.PNG)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """ 收集测试结果（全部测试用例执行完成后，执行一次）, 并写入文件 """
    mydict = {}
    mydict['total'] = terminalreporter._numcollected
    mydict['deselected'] = len(terminalreporter.stats.get("deselected", []))
    mydict['selected'] = terminalreporter._numcollected - len(terminalreporter.stats.get("deselected", []))
    mydict['passed'] = len([i for i in terminalreporter.stats.get("passed", []) if i.when not in ('teardown', 'setup')])
    mydict['failed'] = len([i for i in terminalreporter.stats.get("failed", []) if i.when not in ('teardown', 'setup')])
    mydict['error'] = len([i for i in terminalreporter.stats.get("error", []) if i.when not in ('teardown', 'setup')])
    mydict['skipped'] = len(
        [i for i in terminalreporter.stats.get("skipped", []) if i.when not in ('teardown', 'setup')])
    mydict['total times'] = f'{time.time() - terminalreporter._sessionstarttime} seconds'
    try:
        with open(ConfPath.REPORT_LOC_DIR + f'/result.txt', 'w', encoding='utf-8') as fp:
            json.dump(mydict, fp, ensure_ascii=False, indent=2)
    except:
        with open(ConfPath.REPORT_LOC_DIR + '/API_result.txt', 'w', encoding='utf-8') as fp:
            json.dump(mydict, fp, ensure_ascii=False, indent=2)


@pytest.fixture(scope='session', autouse=True)
def install():
    """ 安装、修改密码 """
    if not conf.is_ide and sys.platform in ('dos', 'win32', 'win16'):
        inst.exe_install('执行 安装')
        inst.click_quick_install('点击 极速安装')
        inst.assert_install_finish('断言 安装完成文字')
        inst.click_close_wizard_tools('点击不开启配置工具')
        inst.click_finish('点击 完成按钮')

        while True:
            resp = requests.get(f'{conf.center_url}/auth/_login')
            log.info(resp.text)
            if '"errno":-1' in resp.text:
                break
            time.sleep(2)

        # 修改密码
        reset_data = {
            'method': 'post',
            'url': f'{conf.center_url}/auth/_reset',
            'json': {"pwd": "admin", "newpwd": "585004c128942a72dae745732429b88d776d88f5"}
        }
        api.http_center('重置密码', reset_data)


@pytest.fixture(scope='session', autouse=True)
def install_linux():
    """ 安装、修改密码 """
    if not conf.is_ide and sys.platform not in ('dos', 'win32', 'win16'):
        path_src = ConfPath.PATH_SRC
        path_dst = ConfPath.PATH_DST
        fo.copy_tree_linux(path_src, path_dst)

        filename, file_path = fo.get_files(path_dst, contain='center-linux')
        center_id = file_path.split('/')[-2]   # /home/test/softs/install/id_30133/center-linux-20.sh
        CmdLine().command('执行 安装-linux', f'expect /home/test/softs/auto_install.sh {center_id}')

        while True:
            resp = requests.get(f'{conf.center_url}/auth/_login')
            log.info(resp.text)
            if '"errno":-1' in resp.text:
                break
            time.sleep(2)
