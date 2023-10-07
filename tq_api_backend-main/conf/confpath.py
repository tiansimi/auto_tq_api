# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 11:23
# @Author : tq
# @File   : confpath.py
import os
import platform
import sys
from multiprocessing import Queue

from utils.functions import json_read


class ConfPath:
    DESKTOP = os.path.join(os.path.expanduser('~'), 'Desktop')
    # 下载路径
    DOWNLOAD = os.path.join(os.path.expanduser('~'), 'Downloads')
    # 工程根目录 D:\HR\hr_api_backend
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 测试用例目录
    CASE_DIR = os.path.join(BASE_DIR, 'cases')

    # 配置文件目录
    CONF_DIR = os.path.join(BASE_DIR, 'conf')
    # libray目录
    LIB_DIR = os.path.join(BASE_DIR, 'library')
    # 测试报告文件目录
    REPORT_DIR = os.path.join(BASE_DIR, 'reports')
    # 切换升级通道工具
    UPGRADE_EXE = os.path.join(LIB_DIR, 'UpdateAssist.exe')
    # 时间同步工具synchronization.bat
    SYNCHRONIZATION = os.path.join(LIB_DIR, 'synchronization.bat')
    # 配置文件
    if sys.platform in ('dos', 'win32', 'win16'):
        CONF_FILE = os.path.join(BASE_DIR, r'conf\config.ini')
        SHARE_FILE = os.path.join(BASE_DIR, r'conf\share.json')
    else:
        CONF_FILE = os.path.join(BASE_DIR, r'conf/config.ini')
        SHARE_FILE = os.path.join(BASE_DIR, r'conf/share.json')
    with open(SHARE_FILE, 'w', encoding='utf-8') as f:
        f.write('{}')

    # log 文件目录
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 图片路径目录
    PATH_DIR = os.path.join(BASE_DIR, 'path')
    # 管理中心配置文件路径
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_SYSCONF = r'C:\Program Files\Huorong\ESCenter\sysconf\center.json'
        if os.path.exists(r'C:\Program Files (x86)'):
            PATH_SYSCONF = r'C:\Program Files (x86)\Huorong\ESCenter\sysconf\center.json'
    else:
        PATH_SYSCONF = r'/opt/apps/huorong/escenter/sysconf/center.json'

    # 卸载路径
    PATH_UNINSTALL = r'"C:\Program Files (x86)\Huorong\ESCenter\uninst.exe"'
    if platform.architecture()[0] == '64bit':
        PATH_UNINSTALL = r'"C:\Program Files (x86)\Huorong\ESCenter\uninst.exe"'
    else:
        PATH_UNINSTALL = r'"C:\Program Files\Huorong\ESCenter\uninst.exe"'

    # 升级目录
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_UPGRADE = r'C:\Program Files (x86)\Huorong\ESCenter\upgrade'
        if platform.architecture()[0] == '64bit':
            PATH_UPGRADE = r'C:\Program Files (x86)\Huorong\ESCenter\upgrade'
        else:
            PATH_UPGRADE = r'C:\Program Files\Huorong\ESCenter\upgrade'
    else:
        PATH_UPGRADE = r'/opt/apps/huorong/escenter/upgrade'

    # 安装目录存储版本信息
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_VERSION = r'C:\Program Files (x86)\Huorong\ESCenter\VERSION'
        if platform.architecture()[0] == '64bit':
            PATH_VERSION = r'C:\Program Files (x86)\Huorong\ESCenter\VERSION'
        else:
            PATH_VERSION = r'C:\Program Files\Huorong\ESCenter\VERSION'
    else:
        PATH_VERSION = r'/opt/apps/huorong/escenter/VERSION'

    # 中心的安装目录
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_ESCenter = r'C:/Program Files (x86)/Huorong/ESCenter'
        if platform.architecture()[0] == '64bit':
            PATH_ESCenter = r'C:/Program Files (x86)/Huorong/ESCenter'
        else:
            PATH_ESCenter = r'C:/Program Files/Huorong/ESCenter'
    else:
        PATH_ESCenter = r'/opt/apps/huorong/escenter/share'
        PATH_ESCenter_1 = r'/opt/apps/huorong/escenter'

    # 安装文件路径
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_SRC = r'\\192.168.3.194\html\ui_ess20_linux\share\安装文件'
        PATH_DST = os.path.join(DESKTOP, '安装文件')
    else:
        PATH_SRC = r'/opt/api_auto2.0/share/安装文件'
        PATH_DST = r'/home/test/softs/install'

    # 本地配置文件
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_CONF = r'c:\softs\conf_local.json'
    else:
        PATH_CONF = r'/home/test/softs/conf_local.json'

    # 测试报告 本地目录
    REPORT_LOC_DIR = os.path.join(BASE_DIR, 'reports')
    if not os.path.exists(REPORT_LOC_DIR):
        os.makedirs(REPORT_LOC_DIR)
    # 测试结果 本地保存路径
    RESULT_LOC_DIR = os.path.join(REPORT_LOC_DIR, 'result')

    # 测试报告 远程目录
    if sys.platform in ('dos', 'win32', 'win16'):
        REPORT_REMOTE_DIR = r'\\192.168.3.194\html\api_auto2.0'
        REPORT_REMOTE_URL = r'http://192.168.3.194:8088/api_auto2.0'
        REMOTE_CONFIG_FILE = r'\\192.168.3.194\html\api_auto2.0\share\conf.json'
        branch = json_read('branch', REMOTE_CONFIG_FILE).strip()
        if branch == 'dev':
            REPORT_REMOTE_DIR = r'\\192.168.3.194\html\api_auto2.0_dev'
            REPORT_REMOTE_URL = r'http://192.168.3.194:8088/api_auto2.0_dev'
    else:
        REMOTE_CONFIG_FILE = r'/opt/api_auto2.0/share/conf.json'
        REPORT_REMOTE_DIR = '/opt/api_auto2.0'
        REPORT_REMOTE_URL = 'http://192.168.3.194:8088/api_auto2.0'
        branch = json_read('branch', REMOTE_CONFIG_FILE).strip()
        if branch == 'dev':
            REPORT_REMOTE_DIR = '/opt/api_auto2.0_dev'
            REPORT_REMOTE_URL = r'http://192.168.3.194:8088/api_auto2.0_dev'

    # center.json配置文件获取上级中心token
    if sys.platform in ('dos', 'win32', 'win16'):
        DOWNLOAD_CENTER_JSON = r'\\192.168.3.194\html\ui_ess20_linux\share\center_json\center.json'
        DOWNLOAD_CENTER_JSON_DESKTOP = os.path.join(DESKTOP, 'center.json')
    else:
        # DOWNLOAD_CENTER_JSON = r'/opt/ui_ess20_linux/share/center_json/center.json'  # Windows中心
        DOWNLOAD_CENTER_JSON = r'/opt/api_auto2.0/share/center_json/center.json'   # linux中心
        PATH_CENTER_JSON_HOME = r'/home/test/softs/'
        DOWNLOAD_CENTER_JSON_DESKTOP = os.path.join(PATH_CENTER_JSON_HOME, 'center.json')
    # 多级中心测试 - 上级中心ip地址
    # SUPERIOR_CENTER_IP = "192.168.3.122"
    # 当前中心ip地址
    LOCAL_CENTER_IP = "127.0.0.1"

    # 导出文件本地地址
    if sys.platform in ('dos', 'win32', 'win16'):
        PATH_EXPORT = r'C:\softs\export'
        MODULES_JSON = r'\\192.168.3.194\html\api_auto2.0\share\modules.json'
    else:
        PATH_EXPORT = r'/home/test/softs/export'
        MODULES_JSON = r'/opt/api_auto2.0/share/modules.json'

    # 文件分发 - 上传文件路径
    if sys.platform in ('dos', 'win32', 'win16'):
        FILE_DISTRIBUTE_FILES = r'\\192.168.3.194\AutoTestData\api_ess20\upload_files'
        FILE_DISTRIBUTE_FILES_UPLOAD = r'\\192.168.3.194\AutoTestData\api_ess20\upload_files'
    else:
        FILE_DISTRIBUTE_BASE_DIR = 'd:/AutoTestData/api_ess20/upload_files'
        FILE_DISTRIBUTE_FILES = r'/home/test/softs/'
        FILE_DISTRIBUTE_FILES_UPLOAD = r'/home/test/softs/upload_files'

class ConfParams:
    # cookies 变量
    COOKIES = {}
    # sc_cookis 上级中心cookies
    SC_COOKIES = {}
    # headers 变量
    HEADERS = {}
    # 上级中心headers
    SC_HEADERS = {}
    # 多级中心 - 上级登录下级 headers
    SC_LOWER_HEADERS = {}
    # 多级中心 - 上级登录下级cookies
    SC_LOWER_COOKIE = {}
    # 心跳上次返回记录
    HEART_BEET_OLD = {}
    # 心跳返回最新记录
    HEART_BEET_NEW = {}
    # 终端队列
    QUE = Queue()
    # 第一次心跳
    HEART_BEET_FIRST = {}
    # 上线确认
    HEART_CONFIRM = {}
    # 保存心跳当前时间
    TIME_HEART_BEET = 1


if __name__ == '__main__':
    print(ConfPath.BASE_DIR)