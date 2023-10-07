# -*- coding:utf-8 -*-
# @Time   : 2022/4/28 14:02
# @Author : tq
# @File   : functions.py
import http.client
import os
import random
import string
import json
import socket

import requests
from filelock import Timeout, FileLock

from jsonpath import jsonpath


def random_int(a, b):
    """ 返回 a, b 之间的随机整数 """

    return random.randint(a, b)


def random_ip():
    """ 返回 1 个随机IP地址 """
    a = str(random.randint(1, 254))
    b = str(random.randint(0, 255))
    c = str(random.randint(0, 255))
    d = str(random.randint(1, 254))

    return '.'.join([a, b, c, d])


def random_str(count, samples=''):
    """
    :param count: 字符串长度
    :param samples: 字符串组成样本集合
    :return: 指定长度的随机字符串
    """
    l = []
    # sample = '0123456789abcdefghijklmnopqrstuvwxyz!@#$%^&*()-+=.'
    sample = random.sample(string.ascii_letters + string.digits, 62)  ## 从a-zA-Z0-9生成指定数量的随机字符： list类型
    # sample = sample + list('!@#$%^&*()-+=.')  # 原基础上加入一些符号元素
    if samples:
        sample = samples

    for i in range(count):
        char = random.choice(sample)  # 从sample中选择一个字符
        l.append(char)

    return ''.join(l)  # 返回字符串


def random_mac():
    """ 随机生成 mac 地址 5C-BA-EF-C7-46-43 """
    l = []
    for i in range(6):
        l.append(random_str(2, '0123456789ABCDEF'))
    return '-'.join(l)


def json_read(jspath, file_path):
    """
    读取 jspath 值
    :param jspath: jsonpath 表达式
    :return: list
    """
    try:
        with open(file_path, 'r') as fp:
            js = json.load(fp)
        result = jsonpath(js, jspath)
        if result:
            return result[0]
        else:
            return result
    except Exception as e:
        print(f'读取json文件错误：{e}')


def json_write(key, value, file_path):
    try:
        # lock = FileLock(file_path + ".lock", timeout=5)
        with FileLock(file_path + ".lock"):
            with open(file_path, 'r', encoding='utf-8') as fp:
                js = json.load(fp)
            js[key] = value
            with open(file_path, 'w', encoding='utf-8') as fp:
                json.dump(js, fp, indent=2, separators=(',', ': '))
    except Exception as e:
        print(f'{e}')


def get_local_center_ip():
    """
    查询本机ip
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def timestamp_change_localtime(change_time):
    """ 时间戳转换为时间 """
    ten_timeArray = time.localtime(change_time)
    ten_otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", ten_timeArray)
    return ten_otherStyleTime


def get_beijing_time(time_format='-'):
    """ 获取 网络北京时间 """
    header = {'User-Agent': 'Mozilla/5.0'}
    url = r'https://www.beijing-time.org/t/time.asp'
    r = requests.get(url=url, headers=header)
    if r.status_code == 200:
        # data = t0=new Date().getTime(); nyear=2022; nmonth=11; nday=14; nwday=1; nhrs=13; nmin=29; nsec=43;
        data = r.text.split(";")

        year = data[1].split('=')[-1]
        month = data[2].split('=')[-1].zfill(2)
        day = data[3].split('=')[-1].zfill(2)
        wday = data[4].split('=')[-1]
        hrs = data[5].split('=')[-1].zfill(2)
        minute = data[6].split('=')[-1].zfill(2)
        sec = data[7].split('=')[-1].zfill(2)
        beijing_time = f"%s{time_format}%s{time_format}%s %s:%s:%s" % (year, month, day, hrs, minute, sec)

        return int(wday), int(hrs), beijing_time
    else:
        return None, None, None

import time
import datetime


class AnyTime:
    # 今天日期 2022-07-21
    today = datetime.date.today()
    # 昨天时间 2022-07-20
    yesterday = today - datetime.timedelta(days=1)
    # 明天时间 2022-07-22
    tomorrow = today + datetime.timedelta(days=1)
    # 后天时间 2022-07-23
    acquire = today + datetime.timedelta(days=2)
    # 昨天开始时间戳 1658246400
    yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d')))
    # 昨天结束时间戳 1658332799
    yesterday_end_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1
    # 今天开始时间戳 1658332800
    today_start_time = yesterday_end_time + 1
    # 今天结束时间戳 1658419199
    today_end_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))) - 1
    # 明天开始时间戳 1658419200
    tomorrow_start_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d')))
    # 明天结束时间戳 1658505599
    tomorrow_end_time = int(time.mktime(time.strptime(str(acquire), '%Y-%m-%d'))) - 1


def setting_time_delay_forward(days=None, hours=None, minutes=None):
    """
    设置当前时间向前或者向后
    :param days: dys为正数表示多加几天，为负数表示减少几天
    :param hours: hours为正数表示多加几小时，为负数表示减少几小时
    :param minutes: minutes为正数表示多加几分钟，为负数表示减少几分钟
    :return:
    """
    if days is not None:
        if days > 0:
            return (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S").split()[
                0]
        else:
            return (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S").split()[
                0]
    elif hours is not None:
        if hours > 0:
            return (datetime.datetime.now() + datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S").split()[1]
        else:
            return (datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S").split()[1]
    else:
        if minutes > 0:
            return (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime(
                "%Y-%m-%d %H:%M:%S").split()[1]
        else:
            return (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime(
                "%Y-%m-%d %H:%M:%S").split()[1]


if __name__ == '__main__':
    # 2024 - 01 - 03 23: 59:59
    s = get_beijing_time()
    print(s)
