# -*- coding:utf-8 -*-
# @Time   : 2022/3/24 19:00
# @Author : tq
# @File   : cmd_line.py
import os
import platform
import re
import subprocess
import allure
import psutil

from utils.log import log


class CmdLine:
    def __init__(self):
        pass

    def command(self, img_info, cmd):
        """ 命令行执行 cmd 命令 """
        try:
            result = os.system(cmd)  # 加 start 不阻塞； linux 系统 后面加 &
            with allure.step(f'执行{img_info}命令：{cmd}'):
                if result == 0:
                    log.info(f'执行成功：{cmd}')
                    allure.attach('成功执行', f'{cmd}')
                else:
                    log.error(f'执行失败：{cmd}')
                    allure.attach('执行失败', f'{cmd}')
                assert not result
        except Exception as e:
            raise e

    def command_popen_text(self, cmd):
        """ 命令行执行 shell 命令，返回命令的输出内容 """
        try:
            s = os.popen(cmd)
            cmd_text = s.buffer.read().decode('utf-8')
            log.info(f"命令返回结果：{cmd_text}")
            return cmd_text
        except Exception as e:
            raise e

    def get_process_info(self, process):
        """ 获取正在运行的进程信息 """
        pid = subprocess.Popen(["pgrep", "-f", process], stdout=subprocess.PIPE, shell=False)
        response = pid.communicate()[0]
        return response

    def get_process_running_linux(self, process):
        """
        获取正在运行的进程
        :param process: 进程名
        :return: 进程名称
        """
        process_list = []
        if platform.system() == 'Linux':
            try:
                res = self.get_process_info(process)
                if res:
                    pid_num = re.findall(r"\d+", str(res))[0]
                    pid_name = psutil.Process(int(pid_num)).name()
                    process_list.append(pid_name)
                    return list(set(process_list))
                else:
                    return []
            except Exception as e:
                return []

    def assert_process_running_linux(self, img_info, process, not_run=False):
        """ 断言 正在运行的进程
        process = hrclient、hipsmain、hipsdaemon
        not_run=False 参数默认进程运行
        """
        pro = self.get_process_running_linux(process)
        with allure.step(f'{img_info} - 期望：{process}。实际：{pro}'):
            if not_run:
                if not pro:
                    log.info(f'断言成功 进程未运行：{process}')
                else:
                    log.info(f'断言失败 进程{process}正在运行，进程：{pro}')
                assert not pro
            else:
                if pro:
                    log.info(f'断言成功 进程{process}正在运行，进程：{pro}')
                else:
                    log.error(f'断言失败 进程未运行：{process}')
                assert pro

    def kill_process_running(self, process):
        """
           结束正在运行的进程
           :param process: 进程名
        """
        if platform.system() == 'Linux':
            res = self.get_process_info(process)
            if res:
                pid_num = re.findall(r"\d+", str(res))[0]
                result = os.system("sudo kill " + pid_num)
                return result
            else:
                return res

    def kill_process(self, process):
        """ 结束进程 """
        with allure.step(f'结束进程{process}'):
            try:
                res = self.kill_process_running(process)
                if res == 0:
                    log.info(f'结束进程【{process}】成功')
                else:
                    log.error(f'结束进程【{process}】失败')
            except Exception as e:
                log.error(f'结束进程【{process}】异常')
                log.error(e)
            assert res == 0


cmd = CmdLine()

if __name__ == '__main__':
    CmdLine().kill_process('')
