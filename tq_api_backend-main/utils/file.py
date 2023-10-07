# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 17:44
# @Author : tq
# @File   : file.py
import os
import stat
import shutil
import json
import time

import xlrd2
from jsonpath import jsonpath

import allure

from conf.confpath import ConfPath
from utils.log import log


class File:
    def __init__(self):
        self.desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

    def file_read(self, file_path):
        """
        读取 文件内容
        :param key:
        :return: list
        """
        with open(file_path, 'r', encoding='UTF-8') as fp:
            file_content = fp.readlines()
        return file_content

    def file_read_excel(self, file_path, exclude_head=False):
        """
        读取 excel文件内容
        :param file_path: 源文件或文件夹路径
        :param exclude_head: 是否移除文件首行标题
        :return:
        """
        data = xlrd2.open_workbook(file_path)  # 打开excel
        table = data.sheets()[0]  # 打开excel的第几个sheet
        nrows = table.nrows  # 捕获到有效数据的行数
        books = []
        for i in range(nrows):
            if exclude_head and i == 0:
                continue
            row = table.row_values(i)  # 获取一行的所有值，每一列的值以列表项存在
            books.append(row)
        return books

    def copy_tree(self, src_path, dst_path):
        """
        拷贝文件或文件夹到其他路径. 特别注意，目的路径如果存在会先删除
        :param src_path: 源文件或文件夹路径
        :param dst_path: 目的文件或文件夹路径
        :return:
        """
        if not os.path.exists(src_path):
            raise ValueError('文件或目录的源路径不存在')

        if os.path.isfile(src_path):
            try:
                shutil.copy(src_path, dst_path)  # 拷贝文件到目的路径
                # shutil.copy2(file_path, dst_path)  # 拷贝文件到目的路径
            except Exception as e:
                log.error(e)
        else:
            if os.path.exists(dst_path):
                if dst_path != ConfPath().DESKTOP:
                    shutil.rmtree(dst_path)
                else:
                    log.info(f'文件夹不能直接指定目录为桌面，需要指定桌面具体的文件夹')
            try:
                shutil.copytree(src_path, dst_path)  # 拷贝文件夹到目的路径
            except shutil.Error as exc:
                raise ValueError(exc)

        with allure.step('拷贝文件'):
            if os.path.exists(src_path):
                log.info(f'成功拷贝 - 文件源路径：{src_path}--目的路径：{dst_path}')
                allure.attach('成功', f'成功拷贝 - 文件源路径：{src_path}\n目的路径：{dst_path}')
            else:
                log.error(f'失败拷贝 - 文件源路径：{src_path}--目的路径：{dst_path}')
                allure.attach('失败', f'失败拷贝 - 文件源路径：{src_path}\n目的路径：{dst_path}')
            assert os.path.exists(dst_path)

    def copy_tree_linux(self, src, dst, su=None):
        """ 拷贝文件或文件夹
        :param src: 源文件路径
        :param dst: 目的文件路径
        :param su: 是否使用sudo执行命令
        :param timeout：
        :return:
        """
        try:
            if su:
                os.system(f'sudo cp -r {src} {dst}')
            else:
                os.system(f'cp -r {src} {dst}')
            assert os.path.exists(dst)
        except Exception as e:
            log.error(f'拷贝失败：{e}')
            return False
        # else:
        #     if os.path.exists(os.path.join(dst, os.path.split(src)[-1])):
        #         log.info(f'成功拷贝 - 文件源路径：192.168.3.194:{src}--目的路径：{dst}')
        #         return True
        #     else:
        #         log.error(f'失败拷贝 - 文件源路径：{src}--目的路径：{dst}')
        #         return False

    def copy_from(self, src, dst, su=None):
        """ 拷贝文件或文件夹 从 window 拷贝到 linux 本地
        :param src: 源文件路径
        :param dst: 目的文件路径
        :param su: 是否使用sudo执行命令
        :return:
        """
        try:
            if su:
                os.system(f'sudo pscp -r -batch -pw Q1w2e3r4 test01@192.168.3.194:{src} {dst}')
            else:
                os.system(f'pscp -r -batch -pw Q1w2e3r4 test01@192.168.3.194:{src} {dst}')
            assert os.path.exists(dst)
        except Exception as e:
            log.error(f'拷贝失败：{e}')
            return False
        else:
            with allure.step('拷贝文件'):
                if os.path.exists(os.path.join(dst, os.path.split(src)[-1])):
                    log.info(f'成功拷贝 - 文件源路径：192.168.3.194:{src}--目的路径：{dst}')
                    allure.attach('成功', f'成功拷贝 - 文件源路径：192.168.3.194:{src}\n目的路径：{dst}')
                else:
                    log.error(f'失败拷贝 - 文件源路径：192.168.3.194:{src}--目的路径：{dst}')
                    allure.attach('失败', f'失败拷贝 - 文件源路径：192.168.3.194:{src}\n目的路径：{dst}')
                assert os.path.exists(os.path.join(dst, os.path.split(src)[-1]))

    def rm_read_only(self, fn, tmp, info):
        if os.path.isfile(tmp):
            os.chmod(tmp, stat.S_IWRITE)
            os.remove(tmp)
        elif os.path.isdir(tmp):
            os.chmod(tmp, stat.S_IWRITE)
            shutil.rmtree(tmp)

    def remove_all(self, file_path):
        """
        删除文件或文件夹
        :param file_path: 文件或文件夹路径。可以直接写文件名，默认指桌面的文件。
        :return:
        """

        # 桌面文件夹路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.desktop, file_path)
        log.debug(f'删除文件路径：{file_path}')

        if os.path.exists(file_path):
            # 删除文件
            if os.path.isfile(file_path):
                os.chmod(file_path, stat.S_IWRITE)
                try:
                    os.remove(file_path)
                except Exception as e:
                    log.error(e)
            # 删除文件夹
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, onerror=self.rm_read_only)
            with allure.step('删除文件'):
                if not os.path.exists(file_path):
                    log.info(f'成功删除文件 - 成功删除文件 - 路径：{file_path}')
                    allure.attach('成功删除', f'成功删除文件 - 路径：{file_path}')
                else:
                    log.error(f'失败删除文件 - 失败删除文件 - 路径：{file_path}')
                    allure.attach('失败删除', f'失败删除文件 - 路径：{file_path}')
        else:
            log.info(f'文件不存在：{file_path}')

    def get_dir(self, dir_path, string):
        """
        获取目录下，特定文件夹
        :param dir_path: 文件夹路径
        :param contain_string: 以字符串开头
        :return: 文件夹名称
        """
        if not os.path.isabs(dir_path):
            dir_path = os.path.join(self.desktop, dir_path)
        files_list = []
        if not os.path.isdir(dir_path):
            print(f'路径为：{dir_path}')
            log.debug(f'路径为：{dir_path}')
            raise ValueError('不是一个合法的目录路径')
        if not isinstance(string, str):
            raise ValueError('extend 必须是字符串！')
        for root, dirs, files in os.walk(dir_path):
            for dir in dirs:
                if dir.startswith(string):
                    return dir
        return 0

    def get_files(self, dir_path, extend=(), contain=None):
        """
        获取目录下，特定扩展名的文件
        :param dir_path: 文件夹路径
        :param extend: 扩展名列表 如 ['.exe','.bat']
        :param contain: 包含
        :return: 文件列表
        """
        if not os.path.isabs(dir_path):
            dir_path = os.path.join(self.desktop, dir_path)
        files_list = []
        if not os.path.isdir(dir_path):
            print(f'路径为：{dir_path}')
            log.debug(f'路径为：{dir_path}')
            raise ValueError('不是一个合法的目录路径')
        if not isinstance(extend, (tuple, list,)):
            raise ValueError('extend 必须是元组或列表类型！')
        if contain:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if contain in file:
                        return file, os.path.join(root, file)
            return 0, 0
        else:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if os.path.splitext(file)[-1] in extend:
                        files_list.append(os.path.join(root, file))
            return files_list

    def get_id_version(self, path):
        """ 获取 path路径的 id 及 版本号 """
        id5 = self.get_dir(path, 'id')
        filename, file_path = self.get_files(path, contain='installer')
        # version = filename.split('-')[1]
        return id5, filename

    def is_exist_path(self, path):
        """ 检测 文件或路径是否存在 """
        if os.path.exists(path):
            return True
        return False

    def get_filesize(self, file_path):
        """
        获取文件或文件夹大小
        :param file_path: 目录全路径
        :return:
        """
        size = 0
        if not os.path.exists(file_path):
            raise ValueError('不是一个合法的文件或文件夹路径')

        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
        else:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    size += os.path.getsize(os.path.join(root, file))
        return size

    def hosts_add(self, text):
        """ 在 hosts 文件中增加一行 """
        try:
            with open(r'C:\Windows\System32\drivers\etc\hosts', 'r', encoding='utf-8') as f:
                txt = f.read()
            if not os.path.exists("C:\\Windows\\System32\\drivers\\etc\\hosts_bak"):
                os.rename("C:\\Windows\\System32\\drivers\\etc\\hosts",
                          "C:\\Windows\\System32\\drivers\\etc\\hosts_bak")
            with open(r'C:\Windows\System32\drivers\etc\hosts', 'w', encoding='utf-8') as f:
                f.write(txt)
                f.write(text)
            log.info('hosts文件，成功增加：{}'.format(text))
        except Exception as e:
            log.error('hosts文件，增加失败：{}'.format(e))

    def hosts_recover(self):
        """ 恢复原来 hosts """
        try:
            if os.path.exists("C:\\Windows\\System32\\drivers\\etc\\hosts"):
                os.remove("C:\\Windows\\System32\\drivers\\etc\\hosts")
            if os.path.exists("C:\\Windows\\System32\\drivers\\etc\\hosts_bak"):
                os.rename("C:\\Windows\\System32\\drivers\\etc\\hosts_bak",
                          "C:\\Windows\\System32\\drivers\\etc\\hosts")
            log.info('hosts文件，成功恢复')
        except Exception as e:
            log.error('hosts文件恢复失败：{}'.format(e))

    def hosts_add_linux(self, text):
        """ 在 hosts 文件中增加一行 """
        try:
            with open(r'/etc/hosts', 'r', encoding='utf-8') as f:
                txt = f.read()
            if not os.path.exists("/etc/hosts_bak"):
                os.rename("/etc/hosts", "/etc/hosts_bak")
            with open(r'/etc/hosts', 'w', encoding='utf-8') as f:
                f.write(txt)
                f.write(text)
            log.info('hosts文件，成功增加：{}'.format(text))
        except Exception as e:
            log.error('hosts文件，增加失败：{}'.format(e))

    def hosts_recover_linux(self):
        """ 恢复原来 hosts """
        try:
            if os.path.exists("/etc/hosts"):
                os.remove("/etc/hosts")
            if os.path.exists("/etc/hosts_bak"):
                os.rename("/etc/hosts_bak", "/etc/hosts")
            log.info('hosts文件，成功恢复')
        except Exception as e:
            log.error('hosts文件恢复失败：{}'.format(e))

    def json_read(self, key, file_path):
        """
        读取 key 值
        :param key:
        :return: list
        """
        with open(file_path, 'r') as fp:
            js = json.load(fp)
        return js.get(key)


fo = File()
if __name__ == '__main__':
    # resp = fo.json_read('$..password', r'C:\softs\test.json')
    resp = fo.get_files("ddd", )
    print(resp)
