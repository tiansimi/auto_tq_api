# -*- coding:utf-8 -*-
# @Time   : 2022/6/23 14:33
# @Author : tq
# @File   : sys_info.py
import sys
import time

import allure
import psutil
if sys.platform in ('dos', 'win32', 'win16'):
    import win32service

from utils.log import log


def checkprocess(processname):
    """ 检查进程 """
    pl = psutil.pids()
    for pid in pl:
        if psutil.Process(pid).name() == processname:
            return pid


def pid_exist(processname, timeout=30):
    endtime = time.time() + timeout
    while True:
        if isinstance(checkprocess(processname), int):
            return True
        else:
            if time.time() > endtime:
                return False
        time.sleep(2)


def stop_win_service(img_info, name):
    with allure.step(img_info):
        scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        handle = win32service.OpenService(scm, name, win32service.SC_MANAGER_ALL_ACCESS)
        try:
            if handle:
                win32service.ControlService(handle, win32service.SERVICE_CONTROL_STOP)
                win32service.CloseServiceHandle(handle)
                log.info(f'停止 {name} 服务成功')
        except Exception as e:
            log.error(e)
            assert 0


def star_win_service(img_info, name):
    """ 启动 """
    with allure.step(img_info):
        scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        handle = win32service.OpenService(scm, name, win32service.SC_MANAGER_ALL_ACCESS)
        try:
            if handle:
                win32service.StartService(handle, None)
                win32service.CloseServiceHandle(handle)
                log.info(f'启动 {name} 服务成功')
        except Exception as e:
            log.error(e)
            assert 0


if __name__ == '__main__':
    print(pid_exist('Calculator.exe'))
