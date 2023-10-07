# -*- coding:utf-8 -*-
# @Time   : 2022/5/17 14:54
# @Author : tq
# @File   : page_install.py
import os
import time
import allure
from utils.opencv import OpenCV
from utils.log import log
from conf.confpath import ConfPath
from utils.file import fo
from utils.cmd_line import CmdLine


class BasePage(OpenCV):
    def __init__(self):
        super(BasePage, self).__init__()

    def click_center(self, img_info, img_path, double=False, click_2=False, right=False):
        """ 单击图片中间位置
        :param img_info: 步骤信息
        :param img_path: 图片路径
        :param click_2: True 两次单击代替双击
        :return:
        """
        self.click_position(img_info, img_path, double=double, click_2=click_2, right=right)

    def click_position(self, img_info, img_path, x_percent=None, y_percent=None,
                       double=False, click_2=False, right=False, move=True):
        """ 单击 图片*percent 的位置，x_percent为横向系数
        :param img_info: 步骤信息
        :param img_path: 图片路径
        :param x_percent: 百分比系数
        :param y_percent: 百分比系数
        :param double: 双击
        :param click_2: True 两次单击 double=True 时生效
        :param right: 右键点击
        :param move: False 表示点击完后，鼠标不移动
        :return:
        """
        with allure.step(f'点击【{img_info}】'):
            loc = self.get_loc_position(img_info, img_path, x_percent=x_percent, y_percent=y_percent)
            try:
                log.debug(f'点击的坐标位置是：{loc}')
                time.sleep(1)
                if right:
                    self.act.to_click_right(*loc)
                    return
                if not double:
                    self.act.to_click(*loc, move=move)
                else:
                    self.act.to_click_double(*loc, click_2=click_2)
                log.info(f'正常点击【{img_info}】--图片路径：{img_path}')
            except Exception as e:
                log.error(f'失败点击【{img_info}】--图片路径：{img_path}')
                log.error(e)

    def send_text(self, img_info, text):
        with allure.step(f'输入【{img_info}】:{text}'):
            try:
                time.sleep(1)
                self.act._send_text(text)
                # self.act.press_keys(['S', 't', 'a', 'r', '-', '1', '0', '2', '2'])
                log.info(f'正常输入【{img_info}】:{text}')
            except Exception as e:
                log.error(f'异常输入【{img_info}】:{text}')
                log.error(e)

    def commond(self, img_info, cmd):
        """ 执行 cmd 命令 """
        CmdLine().command(img_info, cmd)


class PageInstall(BasePage):
    def __init__(self):
        super(PageInstall, self).__init__()

    def exe_install(self, info):
        """ 执行安装 """
        path_src = ConfPath.PATH_SRC
        path_dst = ConfPath.PATH_DST
        fo.copy_tree(path_src, path_dst)
        time.sleep(1)
        filename, file_path = fo.get_files(path_dst, contain='installer')
        self.commond(info, f'start {file_path}')

    def click_quick_install(self, info):
        """ 点击极速安装 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_install/quick_install2.png')
        self.assert_match('等待极速安装按钮', path, timeout=10)
        self.click_center(info, path)

    def assert_install_finish(self, info):
        """ 断言安装完成文字 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_install/install_finish2.png')
        self.assert_match(info, path, timeout=10)

    def click_finish(self, info):
        """ 点击完成按钮 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_install/finish2.png')
        self.click_center(info, path)

    def click_close_wizard_tools(self, info):
        """ 点击 不打开配置向导工具 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_install/open_wizard_tools.png')
        self.assert_match("断言 打开配置向导工具存在", path, timeout=2)
        self.click_center(info, path)


class PageUninstall(BasePage):
    """ 卸载  """

    def __init__(self):
        super(PageUninstall, self).__init__()

    def exe_uninstall(self, info):
        """ 执行卸载 """
        uninstall_path = ConfPath.PATH_UNINSTALL
        time.sleep(1)
        self.commond(info, uninstall_path)

    def click_uninstall_immediately(self, info):
        """ 点击 立即卸载 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_unistall/uninstall_immediately.png')
        self.assert_match('断言 出现立即卸载的弹窗', path, timeout=10)
        self.click_center(info, path)

    def assert_uninstall_finish(self, info):
        """ 断言 卸载完成 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_unistall/uninstall_finish.png')
        time.sleep(0.5)
        self.assert_match(info, path, timeout=30)

    def click_uninstall_finish(self, info):
        """ 点击 卸载完成 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_unistall/uninstall_finish.png')
        time.sleep(0.5)
        self.assert_match("断言 完成按钮存在", path, timeout=5)
        self.click_center(info, path)

    def click_keep_the_configuration(self, info):
        """ 点击 保留中心关键配置 """
        path = os.path.join(ConfPath.PATH_DIR, 'path_unistall/keep_the_configuration.png')
        self.assert_match('断言 保留中心关机配置存在', path, timeout=10)
        self.click_center(info, path)


if __name__ == '__main__':
    # PageInstall().click_quick_install('dianji')
    PageInstall().exe_install('lll')
