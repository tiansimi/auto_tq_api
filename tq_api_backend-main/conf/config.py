# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 11:23
# @Author : tq
# @File   : config.py
"""
读取配置文件
"""
import json
import os
import sys

from configparser import ConfigParser
from conf.confpath import ConfPath, ConfParams
from utils.functions import json_read

conf_file = ConfPath.CONF_FILE


class Config:
    """ 配置文件的封装 """
    __instance = None

    def __init__(self):
        self.config = ConfigParser()
        if not os.path.exists(conf_file):
            raise FileNotFoundError("请确保配置文件存在！！")
        self.load_file()

        self.process_cnt = 1  # 启动多个终端
        self.cid_list = [f'57012416FAA6968A5CD0AC316289810600000{str(c)}' for c in range(100, self.process_cnt + 100)]
        for c in range(100, self.process_cnt + 100):
            ConfParams.QUE.put(f'57012416FAA6968A5CD0AC316289810600000{str(c)}')

        self.cid_list_win1 = ['AC653B791C888D94093F37AC55BEA4D600000000']  # windows 1.0终端
        self.cid_list_linux = ['4FF902ECDBFD17071147C85D14E48D5600000000']
        self.cid_list_mac = ['70B0BCD37910B3575618F6121B48EACB00000000']
        # self.cid_list_linux = [f'4FF902ECDBFD17071147C85C14E48D5600000000' for c in range(100, self.process_cnt + 100)]
        # for c in range(100, self.process_cnt + 100):
        #     ConfParams.QUE.put(f'4FF902ECDBFD17071147C85C14E48D5600000000')

        self.host_ip = json_read('$..host_ip', ConfPath.REMOTE_CONFIG_FILE)
        self.vertest = json_read('$..vertest', ConfPath.REMOTE_CONFIG_FILE)

        self.vm_name = json_read('$..vm_name', ConfPath.PATH_CONF)
        self.key = json_read('$..key', ConfPath.PATH_CONF)
        self.pw = json_read('$..pw', ConfPath.PATH_CONF)

        try:
            with open(ConfPath.MODULES_JSON, 'r', encoding='utf-8') as fp:
                js = json.load(fp)
            modules = ['c{}'.format(module) for module in js if js[module].get('state') == 2]
            self.modules_case = ' or '.join(modules)
        except Exception as e:
            raise ValueError('读取{}出错{}'.format(ConfPath.MODULES_JSON, e))

        # [log]
        self.level = self.get_conf('log', 'LEVEL')

        # [url]
        self.url_ip = self.get_conf('url', 'url_ip')
        # [url_sc] 多级中心，上级中心ip
        if sys.platform in ('dos', 'win32', 'win16'):
            # 注意调整center.json文件获取位置，Windows中心地址为：\\192.168.3.194\html\ui_ess20_linux\share\center_json
            self.url_sc_ip = self.get_conf('url', 'url_sc_ip')
        else:
            # 注意调整center.json文件获取位置，linux中心地址为：\\192.168.3.194\html\api_auto2.0\share\center_json
            self.url_sc_ip = json_read('center_ip', ConfPath.REMOTE_CONFIG_FILE)

        # [system]
        self.time_heart_beet = self.get_conf('system', 'time_heart_beet')

        self.center_url = f'http://{self.url_ip}:8080'
        self.client_url = f'http://{self.url_ip}:80'
        self.sc_center_url = f'http://{self.url_sc_ip}:8080'
        self.sc_client_url = f'http://{self.url_sc_ip}:80'


        # 数据库配置
        self.db_password = json_read('$..database.password', ConfPath.PATH_SYSCONF)
        self.db_info_hress = {'host': self.url_ip, 'port': 3306, 'user': 'root', 'password': self.db_password,
                              'database': 'hress'}
        self.db_info_hress_extra = {'host': self.url_ip, 'port': 3306, 'user': 'root', 'password': self.db_password,
                                    'database': 'hress_extra'}

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        return cls.__instance

    def load_file(self):
        """
        打开配置文件
        :return:
        """
        try:
            self.config.read(conf_file, encoding='UTF-8')
        except Exception as e:
            print("打开配置文件失败！！！")
            raise e

    def get_conf(self, section, option):
        """
        配置文件读取
        :param section:
        :param option:
        :return:
        """
        try:
            param = self.config.get(section, option)
            return param
        except Exception as e:
            print('获取配置文件参数值失败')
            raise e

    def set_conf(self, section, option, value):
        """
        配置文件修改
        :param section: [param]
        :param option: msc_no
        :param value: 1
        :return:
        """
        if not isinstance(value, str):
            value = str(value)
        self.config.set(section, option, value)
        try:
            with open(conf_file, "w+", encoding='utf-8') as fp:
                self.config.write(fp)
        except ImportError as e:
            print("写入配置文件错误！！！")
            raise e

    @property
    def is_ide(self):
        """
        不加参数 返回 True
        :return:
        """
        try:
            s = sys.argv[1]
            return False
        except:
            return True

    def get_json_data(self, file_path):
        """ 获取json数据 """
        with open(file_path, 'rb') as f:  # 使用只读模型，并定义名称为f
            params = json.load(f)  # 加载json文件中的内容给params
            # params["imp"][0]["deeplink"] = "end"  # imp字段对应的deeplink的值修改为end
            # print("修改后的值", params["imp"][0]["deeplink"])  # 打印
        return params  # 返回修改后的内容

    def write_json_data(self, file_path, params):
        """ 写入json文件# 使用写模式，名称定义为r """
        try:
            with open(file_path, 'w') as r:
                # 将params写入名称为r的文件中
                json.dump(params, r)
                print(f'写入json文件成功！')
        except ImportError as e:
            print("写入json文件成功！！！")
            raise e


conf = Config()

if __name__ == '__main__':
    print(conf.is_ide)
