# -*- coding:utf-8 -*-
# @Time   : 2022/3/24 16:47
# @Author : tq
# @File   : action.py
import sys
import time

import pyperclip

if sys.platform in ('dos', 'win32', 'win16'):
    import autoit
    import win32api, win32con
    import pyautogui
from PIL import ImageGrab


class Action:

    def screen(self, png_name):
        """ 截取屏幕 """
        # 获取当前分辨率下的屏幕尺寸
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        # 全屏幕截图
        img = ImageGrab.grab(bbox=(0, 0, width, height))
        # 保存截图
        img.save(png_name)

    def to_click(self, x, y, move=True):
        """
        鼠标移动到位置，单击再移动走
        :param x: 横坐标
        :param y: 纵坐标
        :param move: 点击完成后是否移走
        :return:
        """
        autoit.mouse_move(x, y, speed=3)
        time.sleep(0.01)
        ret = autoit.mouse_click()
        if move:
            autoit.mouse_move(1, 1, speed=3)

    def _send_text(self, text):
        """ 输入 text
        :param text: 输入的文字
        :return:
        """
        pyperclip.copy(text)
        self._delete_all()
        self.send_keys('ctrl', 'v')

    def _delete_all(self):
        self.send_keys('ctrl', 'a')
        self.press_keys(['delete'])

    def send_keys(self, *args):
        """ 发送热键 如：pyautogui.hotkey("win","d")"""
        pyautogui.hotkey(*args)

    def press_keys(self, key):
        """
        按一次 按键
         pyautogui.press(['c', 'h', 'e', 'n'])
         pyautogui.press('shift') # 切换输入法的中英文
        :param key:
        :return:
        """
        pyautogui.press(key)


if __name__ == '__main__':
    import os
    from conf.confpath import ConfPath
    Action().screen(os.path.join(ConfPath.PATH_DIR, 'zz.png'))