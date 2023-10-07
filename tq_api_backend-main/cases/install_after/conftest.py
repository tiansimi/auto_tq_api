# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 16:34
# @Author : tq
# @File   : conftest.py
import time
import pytest

from jsonpath import jsonpath

from conf.config import conf
from conf.confpath import ConfParams, ConfPath
from utils.assert_api import AssertApi
from utils.base_api import BaseApi
from utils.client import ClientThread

re_api = BaseApi()


def assets_items():
    """ 设置资产登记信息，下发资产登记时使用 """
    # 登记信息管理
    js_data = {
        'method': 'post',
        'url': '/mgr/assets_items/_list',
        'json': {"view":{"begin":0,"count":15}}
    }
    ret = re_api.http_center('资产登记-获取登记信息列表', js_data)

    if jsonpath(ret, '$..total')[0] == 0:
        # 必填项，下拉列表形式
        js_data = {
            'method': 'post',
            'url': '/mgr/assets_items/_create',
            'json': {"label": "办公用品", "empty": 0, "input": "select", "option": "", "options": ["鼠标", "显示屏", "笔记本电脑"]}
        }
        re_api.http_center('添加资产登记-必填项下拉列表形式', js_data)

        # 必填项，输入框形式
        js_data = {
            'method': 'post',
            'url': '/mgr/assets_items/_create',
            'json': {"label": "办公用品使用情况", "empty": 0, "input": "text", "option": "", "options": []}
        }
        re_api.http_center('添加资产登记-必填项输入框形式', js_data)

        # 非必填项，下拉列表形式
        js_data = {
            'method': 'post',
            'url': '/mgr/assets_items/_create',
            'json': {"label": "其他用品", "empty": 1, "input": "select", "option": "", "options": ["水杯", "心相印纸巾", "插线板"]}
        }
        re_api.http_center('添加资产登记-非必填项下拉列表形式', js_data)

        # 非必填项，输入框形式
        js_data = {
            'method': 'post',
            'url': '/mgr/assets_items/_create',
            'json': {"label": "其他用品剩余数量", "empty": 1, "input": "text", "option": "", "options": []}
        }
        re_api.http_center('添加资产登记-非必填项输入框形式', js_data)


@pytest.fixture(scope='session', autouse=True)
def get_header():
    """ 获取 headers cookies """
    data = {
        'method': 'post',
        'url': '/auth/_login',
        'json': {"username": "admin", "password": "585004c128942a72dae745732429b88d776d88f5", "remember": True}
    }
    resp = re_api.http_center('获取COOKIES', data, body=False)

    ConfParams.HEADERS = {
        'HTTP-CSRF-TOKEN': resp.cookies.get('HRESSCSRF'),
        'Origin': conf.center_url
    }
    ConfParams.COOKIES = dict(resp.cookies)


@pytest.fixture(scope='session', autouse=True)
def query_license_info():
    """ 查询授权信息 - 未授权状态"""
    if not conf.is_ide:
        json_data = {
            "method": "get",
            "url": "/mgr/license/_info"
        }
        resp = re_api.http_center('未授权状态', json_data)
        time.sleep(2)
        assert_dict = dict(zip(["nodes_num", "status", "type"], [0, 0, 0]))
        AssertApi().assert_keys_values('断言windows设备中终端设备为0，可用状态也为0', resp, assert_dict, list_path='$..windows')
        AssertApi().assert_keys_values('断言linux设备中终端设备为0，可用状态也为0', resp, assert_dict, list_path='$..linux')
        AssertApi().assert_keys_values('断言linux_desktop设备中终端设备为0，可用状态也为0', resp, assert_dict, list_path='$..linux_desktop')
        AssertApi().assert_keys_values('断言macos设备中终端设备为0，可用状态也为0', resp, assert_dict, list_path='$..macos')
        AssertApi().assert_key_value('断言不存在授权码', resp, '$..serial', "")


@pytest.fixture(scope='session', autouse=True)
def send_accredit():
    """ 进行授权操作 """
    if not conf.is_ide:
        data = {"password": conf.pw,"serial": conf.key, "serial_password": conf.pw}
        js_data = {
            'method': 'post',
            'url': '/mgr/license/_ato',
            'json': data
        }
        re_api.http_center('授权', js_data)
        time.sleep(2)


@pytest.fixture(scope='session', autouse=True)
def settings():
    """ 设置 手动升级及心跳间隔5分钟 """
    if not conf.is_ide:
        # 调整心跳
        js_data = {
            'method': 'post',
            'url': '/mgr/sysconf/_limit',
            'json': {"concurrent_max": 0, "download_speed_KBs": 0, "heartbeat_sec": 300, "is_auto": 0}
        }
        re_api.http_center('心跳调整手动，300秒', js_data)
        js_data = {
            'method': 'post',
            'url': '/mgr/sysconf/_log',
            'json': {"expire_month": 6}
        }
        re_api.http_center('日志', js_data)
        js_data = {
            'method': 'post',
            'url': '/mgr/sysconf/_syslog',
            'json': {"enable": False, "clint_security_log": True, "center_update_log": True, "leakrepair_log": True}
        }
        re_api.http_center('日志', js_data)

        # 改为手动升级
        js_data2 = {
            'method': 'post',
            'url': '/mgr/sysconf/_upgrade',
            'json': {"method": 1, "proxy": {"enable": False, "addr": "", "port": 0, "username": "", "password": ""}}
        }
        re_api.http_center('改为手动升级', js_data2)

    # 设置资产登记信息，下发资产登记时使用
    assets_items()


@pytest.fixture(scope='session', autouse=True)
def start_client():
    for cid in conf.cid_list:
        time.sleep(5)
        c = ClientThread(cid)
        c.setDaemon(True)
        c.start()
