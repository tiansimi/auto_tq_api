# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 17:14
# @Author : tq
# @File   : log.py

"""
日志记录
级别	    | 何时使用
DEBUG   ：详细信息，一般只在调试问题时使用。
INFO    ：证明事情按预期工作。
WARNING ：某些没有预料到的事件的提示，或者在将来可能会出现的问题提示。例如：磁盘空间不足。但是软件还是会照常运行。
ERROR   ：由于更严重的问题，软件已不能执行一些功能了。
CRITICAL：严重错误，表明软件已不能继续运行了。
"""

import os

import logging
from conf.config import conf
from conf.confpath import ConfPath


def create_file(filename):
    path = filename[0:filename.rfind('\\')]
    if not os.path.isdir(path):
        os.makedirs(path)
    if not os.path.isfile(filename):
        with open(filename, mode='w', encoding='utf-8'):
            pass


class HandleLogger:
    """处理日志相关的模块"""
    __instance = None

    def __init__(self):
        self.log_file = os.path.join(ConfPath.LOG_DIR, 'log.log')
        self.err_file = os.path.join(ConfPath.LOG_DIR, 'err.log')
        create_file(self.log_file)
        create_file(self.err_file)

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        return cls.__instance

    def create_logger(self):
        """ 创建日志收集器
        :return: 日志收集器
        """

        # 第一步：创建一个日志收集器
        log = logging.getLogger("hr")

        # 第二步：设置收集器收集的等级
        log.setLevel(conf.level)

        # 第三步：设置输出渠道以及输出渠道的等级
        """ 写入文件，如果文件超过200M，仅保留5个文件。200M=524288000Bytes(字节)
        # fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=209715200, backupCount=5, encoding='utf-8')
        """
        fh = logging.FileHandler(self.log_file, encoding="utf8")
        # fh.setLevel(conf.fh_level)
        log.addHandler(fh)

        eh = logging.FileHandler(self.err_file, encoding="utf8")
        eh.setLevel('ERROR')
        log.addHandler(eh)

        sh = logging.StreamHandler()
        # sh.setLevel(conf.sh_level)
        log.addHandler(sh)

        # 创建一个输出格式对象
        formats = '%(asctime)s -- [%(filename)s-->line:%(lineno)d] - %(levelname)s: %(message)s'
        form = logging.Formatter(formats)

        # 将输出格式添加到输出渠道
        fh.setFormatter(form)
        eh.setFormatter(form)
        sh.setFormatter(form)

        return log


log = HandleLogger().create_logger()