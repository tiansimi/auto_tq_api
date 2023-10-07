# -*- coding:utf-8 -*-

# -*- coding:utf-8 -*-
# @Time   : 2021/12/21 17:10
# @Author : tq
# @File   : regedit_operrate.py
'''
    key = winreg.OpenKeyEx(winreg.HKEY_CLASSES_ROOT, r"")
    #创建新的键
    newKey = winreg.CreateKey(key,"aTest")
    #给新创建的键添加键值
    winreg.SetValueEx(newKey,"a1",0,winreg.REG_EXPAND_SZ,"aaa")
    winreg.SetValueEx(newKey,"b1","star",1, "bbb")
    #创建新的子键
    key = winreg.OpenKeyEx(winreg.HKEY_CLASSES_ROOT, r"aTest")
    newKey = winreg.CreateKey(key,"DefaultIcon")
    winreg.SetValueEx(newKey,"",0,winreg.REG_EXPAND_SZ, "path ,1")

    newKey = winreg.CreateKey(key,"shell")
    key = winreg.OpenKeyEx(winreg.HKEY_CLASSES_ROOT, r"aTest\shell")
    newKey = winreg.CreateKey(key,"open")
    key = winreg.OpenKeyEx(winreg.HKEY_CLASSES_ROOT, r"aTest\shell\open")
    newKey = winreg.CreateKey(key,"command")
    winreg.SetValueEx(newKey,"url",0,winreg.REG_EXPAND_SZ, "\"path\" \"%1\"")
'''
import sys

if sys.platform in ('dos', 'win32', 'win16'):
    import winreg
from utils.log import log


def get_reg_value(reg_key, name=''):
    """
    获取 注册表中 对应名称的数据
    :param reg_key: 注册表全路径
    :param name: 键值名称
    :return: 键值数据
    """
    key = reg_key.split('\\', maxsplit=1)[0]
    sub_key = reg_key.split('\\', maxsplit=1)[1]
    p_key = getattr(winreg, key)

    try:
        handle = winreg.OpenKey(p_key, sub_key, 0)
        value, _type = winreg.QueryValueEx(handle, name)
    except Exception as e:
        log.error(f'未成功获取注册表信息 - 注册表键为：{reg_key}\n键名：{name}')
        raise ValueError(f'获取注册表信息:{reg_key}出错:{e}')
    else:
        log.info(f'成功获取注册表信息 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')
        return value


def create_key(reg_key, name, value):
    """
    在存在的 reg_key 创建键值对 （注册表键不存在还未考虑，以后完善）
    :param reg_key: 注册表键 （已存在的）
    :param name: 键名
    :param value: 键值
    :return:
    """
    key = reg_key.split('\\', maxsplit=1)[0]
    sub_key = reg_key.split('\\', maxsplit=1)[1]
    p_key = getattr(winreg, key)
    if not is_reg_value(reg_key, name):
        with winreg.CreateKeyEx(p_key, sub_key, 0) as key: pass
    handle = winreg.OpenKeyEx(p_key, sub_key, 0, access=winreg.KEY_ALL_ACCESS)  # winreg.KEY_ALL_ACCESS 赋予权限
    # 创建新的键

    # newKey = winreg.CreateKey(key, "aTest")
    # 给新创建的键添加键值
    winreg.SetValueEx(handle, name, 0, winreg.REG_DWORD, value)
    try:
        value = get_reg_value(reg_key, name)
        log.info(f'正常添加 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')
    except:
        log.error(f'未正常添加 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')
        raise ValueError(f'未正常添加 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')


def delete_key(reg_key, name):
    """
    删除已存在的 键值对
    :param reg_key: 注册表键 （已存在的）
    :param name: 键名
    :param value: 键值
    :return:
    """
    key = reg_key.split('\\', maxsplit=1)[0]
    sub_key = reg_key.split('\\', maxsplit=1)[1]
    p_key = getattr(winreg, key)
    if is_reg_value(reg_key, name):
        keyee = winreg.OpenKeyEx(p_key, sub_key, 0, access=winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(keyee, name)
    else:
        log.info(f'键值对不存在 - 注册表键为：{reg_key}\n键名：{name}')
        return
    if is_reg_value(reg_key, name):
        log.error(f'未删除成功键值对 - 注册表键为：{reg_key}\n键名：{name}')
        raise ValueError(f'未删除成功键值对 - 注册表键为：{reg_key}\n键名：{name}')
    else:
        log.info(f'已成功删除键值对 - 注册表键为：{reg_key}\n键名：{name}')


def create_key_type(reg_key, name, type, value):
    """
    在存在的 reg_key 创建键值对 （注册表键不存在还未考虑，以后完善）
    :param reg_key: 注册表键 （已存在的）
    :param name: 键名
    :param value: 键值
    :return:
    """
    key = reg_key.split('\\', maxsplit=1)[0]
    sub_key = reg_key.split('\\', maxsplit=1)[1]
    p_key = getattr(winreg, key)
    if not is_reg_value(reg_key, name):
        with winreg.CreateKeyEx(p_key, sub_key, 0) as key: pass
    handle = winreg.OpenKeyEx(p_key, sub_key, 0, access=winreg.KEY_ALL_ACCESS)  # winreg.KEY_ALL_ACCESS 赋予权限
    # 创建新的键

    # newKey = winreg.CreateKey(key, "aTest")
    # 给新创建的键添加键值
    winreg.SetValueEx(handle, name, 0, type, value)
    try:
        value = get_reg_value(reg_key, name)
        log.info(f'正常添加 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')
    except:
        log.error(f'未正常添加 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')
        raise ValueError(f'未正常添加 - 注册表键为：{reg_key}\n键名：{name} - 键值：{value}')


def is_reg_value(reg_key, name):
    """
    判断 注册表中是否存在 键值
    :param reg_key: 注册表全路径
    :param name: 键值名称
    :return: 键值数据
    """
    key = reg_key.split('\\', maxsplit=1)[0]
    sub_key = reg_key.split('\\', maxsplit=1)[1]
    p_key = getattr(winreg, key)

    try:
        handle = winreg.OpenKey(p_key, sub_key, 0)
        value, _type = winreg.QueryValueEx(handle, name)
    except:
        log.debug(f'判断注册表没有键值对 - 注册表键为：{reg_key}\n键名：{name}')
        return False
    else:
        log.debug(f'判断注册表存在键值对 - 注册表键为：{reg_key}\n键名：{name}')
        if value == 0:
            return '0'
        return value
