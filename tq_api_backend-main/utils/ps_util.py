# -*- coding:utf-8 -*-
# @Time   : 2021/12/1 14:39
# @Author : tq
# @File   : ps_util.py
import os
import re
import sys
import time
import psutil
import socket
if sys.platform in ('dos', 'win32', 'win16'):
    from ctypes import windll
    import wmi

from utils.log import log
from utils.regedit_operrate import get_reg_value, is_reg_value


def get_pid(process_name):
    """
    根据 pid名字模糊匹配，获取 pid 号
    :param process_name:
    :return:
    """
    pids = psutil.process_iter()
    for pid in pids:
        if process_name in pid.name():
            return pid.pid


def get_cpu_state():
    """
    获取 系统 CPU 平使用率
    :return: CPU使用率
    """
    ps = psutil.cpu_percent(1)
    return int(ps)
    #     if
    # time.sleep(count-5)
    # cpu = 0
    # for i in range(5):
    #     cpu += psutil.cpu_percent(1)
    # return cpu // 5


def kill_pid(id):
    p = psutil.Process(id)
    p.terminate()


def get_pid_cpu_state(pid):
    """
    根据 pid 获取进程 cpu 使用率
    :param pid:
    :return:
    """
    if pid:
        process = psutil.Process()
        time.sleep(5)
        cpu = 0
        for i in range(5):
            cpu += process.cpu_percent(1)
        return cpu // 5


class Psutil:
    def __init__(self):
        if sys.platform in ('dos', 'win32', 'win16'):
            self.c = wmi.WMI()

    @property
    def host_ip(self):
        """
        查询本机ip地址
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

    @property
    def system_version(self) -> str:
        """ 返回 系统版本 如：Windows 10"""
        for info in self.c.Win32_OperatingSystem():
            # return ' '.join(info.Caption.split()[1:3])
            return info.Caption


    @property
    def system_bit(self) -> str:
        """ 返回 系统位数 如：64 或 32 """
        for info in self.c.Win32_OperatingSystem():
            return info.OSArchitecture[0:2]

    @property
    def system_display_version(self) -> str:
        """ 返回 系统版本文字 如：专业版 """
        for info in self.c.Win32_OperatingSystem():
            return ''.join(info.Caption.split()[-1])

    @property
    def system_build_number(self) -> str:
        """ 返回 系统 BuildNumber 如： 19043 """
        for info in self.c.Win32_OperatingSystem():
            return info.BuildNumber

    @property
    def system_name(self) -> str:
        """ 返回 系统版本文字 如：Windows_10_专业版_64_位_21H1 """
        system = ''
        windows_version = [' '.join(info.Caption.split()[1:3]) for info in ps.c.Win32_OperatingSystem()][0]
        for info in self.c.Win32_OperatingSystem():
            system1 = '_'.join(info.Caption.split()[1:4] + [info.OSArchitecture.split()[0]])
            system = system1.replace('专业版', 'professional').replace('企业版', 'edition').replace('旗舰版', 'ultimate')
        if windows_version == 'Windows 10' and self.system_bit == '64':
            base_key = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
            if is_reg_value(base_key, 'DisplayVersion'):
                version = get_reg_value(base_key, name='DisplayVersion')
                return '_'.join([system, version])
            if is_reg_value(base_key, 'ReleaseId'):
                version = get_reg_value(base_key, name='ReleaseId')
                return '_'.join([system, version])
        if self.system_build_number == '10240':
            build_number = '1507'
        else:
            build_number = self.system_build_number

        ret = '_'.join([system, build_number])
        return ret

    @property
    def is_ide(self):
        """
         判断是否 ide 执行
        :return: 0：ide执行； 1：其他执行
        """
        hwnd = windll.user32.GetForegroundWindow()  # 当前活动窗口
        out = windll.kernel32.GetStdHandle(-0xb)  # stdin: 0xa, stdout: 0xb, stderr: 0xc 获取标准输出
        rtn = windll.kernel32.SetConsoleTextAttribute(out, 0x7)  # 设置颜色 ide中设置返回0 其他返回1
        return rtn

    def get_process_running(self, process):
        """
        获取正在运行的进程
        :param process: 进程名 或 进程列表
        :return: (长度, 进程名或进程列表)
        """
        process_list = []
        if isinstance(process, str):
            for pro in self.c.Win32_Process(name=process):
                process_list.append(pro.Name)
                return list(set(process_list))
        if isinstance(process, (list, tuple)):
            for pro in process:
                for p in self.c.Win32_Process(name=pro):
                    process_list.append(p.Name)
            return list(set(process_list))
        return []

    def get_process_startup(self, process):
        """
        获取自启动中进程
        :param process:
        :return:
        """
        process_list = []
        if isinstance(process, str):
            for pro in self.c.Win32_StartupCommand():
                if process in pro.Command:
                    process_list.append(process)
                    return process_list
        if isinstance(process, (list, tuple)):
            for p in process:
                for pro in self.c.Win32_StartupCommand():
                    if p in pro.Command:
                        process_list.append(p)
                        return process_list
        return []

    def get_driver_running(self, drivers):
        """
        获取正在运行的驱动
        :param drivers: 驱动名 或 驱动列表
        :return: (长度, 进程名或进程列表)
        """
        driver_list = []
        if isinstance(drivers, str):
            for driver in self.c.Win32_SystemDriver(State='Running', Name=re.split('[_.]', drivers)[0]):
                if drivers in driver.PathName:
                    driver_list.append(drivers)
                return driver_list
        if isinstance(drivers, (list, tuple)):
            for d in drivers:
                for driver in self.c.Win32_SystemDriver(State='Running', Name=re.split('[_.]', d)[0]):
                    if d in driver.PathName:
                        driver_list.append(d)
            return driver_list
        return []

    def get_service_running(self, service_name):
        """
        获取当前系统运行
        :param process: 服务名 或 服务列表
        :return: (长度, 服务名或服务列表)
        """
        service_list = []
        if isinstance(service_name, str):
            for pro in self.c.Win32_Service(name=service_name):
                service_list.append(pro.Name)
                return list(set(service_list))
        if isinstance(service_name, (list, tuple)):
            for pro in service_name:
                for p in self.c.Win32_Service(name=pro):
                    service_list.append(p.Name)
            return list(set(service_list))
        return []


ps = Psutil()


if __name__ == '__main__':
    print(ps.get_process_running("Wizard.exe"))
    os.system("taskkill /f /im Wizard.exe")
