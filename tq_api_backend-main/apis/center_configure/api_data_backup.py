# -*- coding:utf-8 -*-
# @Time   : 2022/11/3 13:08
# @Author : cyq
# @File   : api_data_backup.py
import os

from utils.base_api import BaseApi


class ApiDataBackup(BaseApi):
    """ 数据备份 """
    def __init__(self):
        super(ApiDataBackup, self).__init__()

    def api_immed_backup(self, info, data):
        """ 立即备份 """
        json_data = {
            "method": "post",
            "url": "/mgr/backup/_backup",
            "json": data
        }
        return self.http_center(info, json_data, iserrno=False)

    def api_del_data_backup(self, info, data):
        """ 删除备份 """
        json_data = {
            "method": "post",
            "url": "/mgr/backup/_delete",
            "json": data
        }
        return self.http_center(info, json_data, iserrno=False)

    def api_query_data_backup(self, info, data):
        """ 备份数据查询 """
        json_data = {
            "method": "post",
            "url": "/mgr/backup/_query",
            "json": data
        }
        return self.http_center(info, json_data)

    def api_data_backup_recover(self, info, data):
        """ 数据恢复 """
        json_data = {
            "method": "post",
            "url": "/mgr/backup/_restore",
            "json": data
        }
        return self.http_center(info, json_data, iserrno=False)

    def api_data_backup_download(self, info, ts, file_path):
        """ 下载备份数据 """
        json_data = {
            "url": f"/mgr/backup/_download?ts={ts}",
        }
        return self.http_center_download_files(info, json_data, file_path)

    def api_data_backup_import(self, info, file_path, memo=''):
        """ 导入备份文件 """
        files = {
            # 'memo': (None, memo),
            # 'name': (None, os.path.split(file_path)[-1]),
            'file': (os.path.split(file_path)[-1], open(file_path, 'rb'), 'multipart/form-data')
        }
        js_data = {
            'method': 'post',
            'url': '/mgr/backup/_import',
            'files': files
        }
        return self.http_center(info, js_data)

    def api_auto_data_backup(self, info, data):
        """ 自动备份 """
        json_data = {
            "method": "post",
            "url": "/mgr/sysconf/_backup",
            "json": data
        }
        return self.http_center(info, json_data, iserrno=False)
