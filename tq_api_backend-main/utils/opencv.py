# -*- coding:utf-8 -*-
# @Time   : 2022/3/24 16:42
# @Author : tq
# @File   : opencv.py
import os
import time

import allure
from cv2 import cv2 as cv
from PIL import ImageGrab
import numpy as np

from utils.action import Action
from conf.confpath import ConfPath
from utils.log import log

THRESHOLD = 0.8


def wait_until_match(timeout=8, threshold=THRESHOLD):
    """ 等待直到图片被匹配
    定义隐式等待 装饰器，提高等待效率问题
    :param timeout: 等待时间 秒数
    :param threshold: 图像匹配阈值 业内默认为 0.8 可以调整
    :return:
    """
    def outer(func):
        def inner(*args, **kwargs):
            end_time = time.time() + timeout
            log.debug(f'开始匹配图片')
            while True:
                # time.sleep(0.5)
                result = func(*args, **kwargs)
                if isinstance(result[2], float):  # 单图片匹配
                    if result[2] > threshold:
                        log.debug(f'已匹配到图片')
                        return result
                    time.sleep(0.5)
                else:  # 多图片匹配
                    time.sleep(1)
                    result = func(*args, **kwargs)
                    loc = np.where(result[2] >= 0.8)
                    pt = [(pt) for pt in zip(*loc)]
                    log.debug(f'识别结果为：{pt}')
                    if pt:
                        log.debug(f'已匹配到多个图片：{pt}')
                        return result
                if time.time() > end_time:
                    break
            log.debug(f'超时{timeout}秒，未匹配到图片:')
            return result
        return inner
    return outer


def wait_until_not_match(timeout=8, threshold=THRESHOLD):
    """ 等待直到图片未被匹配
    定义隐式等待 装饰器，提高等待效率问题
    :param timeout: 等待时间 秒数
    :param threshold: 图像匹配阈值 业内默认为 0.8 可以调整
    :return:
    """
    def outer(func):
        def inner(*args, **kwargs):
            start_time = time.time()
            end_time = time.time() + timeout
            log.info(f'开始验证未匹配到图片')
            while True:
                result = func(*args, **kwargs)
                if result[2] < threshold:
                    log.info(f'确定未匹配到图片。花费时间:{time.time() - start_time} 秒')
                    return result
                time.sleep(0.5)
                if time.time() > end_time:
                    break
            log.info(f'超时{timeout}秒，一直能匹配到图片')
            return result
        return inner
    return outer


class OpenCV:
    def __init__(self):
        self.src_img = os.path.join(ConfPath.PATH_DIR, 'zz_screen.png')
        self.act = Action()

    def savescreen(self, png_name='zz_screen.png'):
        """ 截取 屏幕 """
        # self.act.screen(os.path.join(ConfPath.PATH_DIR, png_name))
        try:
            im = ImageGrab.grab(include_layered_windows=True)
            im.save(os.path.join(ConfPath.PATH_DIR, png_name))
        except:
            im = ImageGrab.grab(include_layered_windows=True)
            im.save(os.path.join(ConfPath.PATH_DIR, png_name))

    def __match_one(self, templ_img):
        """ 匹配单个最匹配的图片
        :param templ_img: 图片路径 如：main_pic\arrows.png
        :return:
        """
        self.savescreen()
        try:
            image = cv.imread(self.src_img)  # 读取屏幕截图图像
            templ = cv.imread(templ_img)  # 读取需匹配图像
        except Exception as e:
            log.error(f'读取图像有误：路径不能包含中文路径.\n错误信息：{e}')
            return 0, 0, 0, 0
        else:
            h, w = templ.shape[:2]  # 获取目标图像大小，用于计算中心点
            ret = cv.matchTemplate(image, templ, cv.TM_CCOEFF_NORMED)  # 应用模板匹配
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(ret)  # max_loc 左上角坐标

            log.debug(f'图像：{templ_img}匹配结果：最大值:{max_val}----左上角坐标：{max_loc}')

            # 返回 图片高度、宽度、最大匹配度、坐标
            return h, w, max_val, max_loc

    def __match_all(self, templ_img):
        """ 匹配所有符合的图片
        :param templ_img: 图片路径 如：main_pic\arrows.png
        :return:
        """

        self.savescreen()
        try:
            image = cv.imread(self.src_img)  # 读取屏幕截图图像
            templ = cv.imread(templ_img)  # 读取需匹配图像
        except Exception as e:
            log.error(f'读取图像有误：路径不能包含中文路径.\n错误信息：{e}')
            return 0, 0, 0
        else:
            h, w = templ.shape[:2]  # 获取目标图像大小，用于计算中心点
            ret = cv.matchTemplate(image, templ, cv.TM_CCOEFF_NORMED)  # 应用模板匹配
            # loc = np.where(ret >= 0.8)

            # 返回 图片高度、宽度、坐标
            return h, w, ret

    @wait_until_match(timeout=15)
    def __match_img(self, templ_img):
        """ 等待匹配图片 最多等待 15 秒 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=60)
    def __match_img1(self, templ_img):
        """ 等待匹配图片 最多等待 1 分钟 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=300)
    def __match_img5(self, templ_img):
        """ 等待匹配图片 最多等待 5 分钟 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=600)
    def __match_img10(self, templ_img):
        """ 等待匹配图片 最多等待 10 分钟 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=1800)
    def __match_img30(self, templ_img):
        """ 等待匹配图片 最多等待 30 分钟 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=3600)
    def __match_img60(self, templ_img):
        """ 等待匹配图片 最多等待 60 分钟 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=2)
    def __is_match_img(self, templ_img):
        """ 判断是否存在图片 """
        return self.__match_one(templ_img)

    @wait_until_not_match()
    def __not_match_img(self, templ_img):
        """ 等待不匹配图片 默认最多等待 8 秒 """
        return self.__match_one(templ_img)

    @wait_until_match(timeout=1)
    def __scrool_match_img(self, templ_img):
        """ 滚动滚轮匹配图片 """
        return self.__match_one(templ_img)

    @wait_until_match()
    def __match_imgs(self, templ_img):
        """ 匹配多个图片 """
        return self.__match_all(templ_img)

    def is_match(self, img_info, templ_img, timeout=0):
        """ 判断是否匹配到图像
        :param templ_img:
        :param timeout: 超时时间。默认:15秒；1、5、10、30 代表分钟
        :return: 未匹配到 返回 False; 匹配到 返回数据
        """
        if timeout == 0:
            h, w, max_val, max_loc = self.__is_match_img(templ_img)
        elif timeout == 1:
            h, w, max_val, max_loc = self.__match_img1(templ_img)
        elif timeout == 5:
            h, w, max_val, max_loc = self.__match_img5(templ_img)
        elif timeout == 10:
            h, w, max_val, max_loc = self.__match_img10(templ_img)
        elif timeout == 30:
            h, w, max_val, max_loc = self.__match_img30(templ_img)
        else:
            h, w, max_val, max_loc = self.__match_img(templ_img)

        if max_val < THRESHOLD:  # 小于0.8时，判断为未找到图像
            log.info(f'判断-图像不存在-匹配阈值：{max_val}-图像【{img_info}】存在--图片路径：{templ_img}')
            return False
        log.info(f'判断-图像存在-匹配阈值：{max_val}-图像【{img_info}】存在--图片路径：{templ_img}')
        return h, w, max_val, max_loc

    def assert_match(self, img_info, templ_img, timeout=0):
        """ 断言 图像存在
        :param img_info: 步骤说明信息
        :param templ_img: 图片路径
        :param timeout: 超时时间。默认:15秒；1、5、10、30 代表分钟
        :return:
        """
        if timeout == 0:
            h, w, max_val, max_loc = self.__match_img(templ_img)
        elif timeout == 1:
            h, w, max_val, max_loc = self.__match_img1(templ_img)
        elif timeout == 5:
            h, w, max_val, max_loc = self.__match_img5(templ_img)
        elif timeout == 10:
            h, w, max_val, max_loc = self.__match_img10(templ_img)
        elif timeout == 30:
            h, w, max_val, max_loc = self.__match_img30(templ_img)
        elif timeout == 60:
            h, w, max_val, max_loc = self.__match_img60(templ_img)
        else:
            h, w, max_val, max_loc = self.__match_img(templ_img)

        with allure.step(f'断言【{img_info}】存在'):
            allure.attach('断言', f'期望结果：大于{THRESHOLD}, 实际结果：{max_val}\n图片路径：{templ_img}')
            if max_val > THRESHOLD:
                log.info(f'断言通过-匹配阈值：{max_val}-图像【{img_info}】存在--图片路径：{templ_img}')
            else:
                log.error(f'断言失败-匹配阈值：{max_val}-图像【{img_info}】不存在--图片路径：{templ_img}')
                self.savescreen('failures.png')
            assert max_val > THRESHOLD

    def get_loc_position(self, img_info, templ_img, x_percent=None, y_percent=None):
        """ 获取唯一匹配图像的坐标
        :param templ_img: 被查找图像路径
        :param x_percent: 横向百分比系数
        :param y_percent: 纵向百分比系数
        :return: 匹配图像中心坐标
        默认返回图像的中心坐标
        x_percent不为空时，返回 (横坐标*x_percent, y中心坐标) 处的坐标
        y_percent不为空时，返回 (x中心坐标，纵坐标*y_percent) 处的坐标
        x_percent 和 y_percent 都不为空时，返回 (横坐标*x_percent，纵坐标*y_percent) 坐标
        """

        h, w, max_val, max_loc = self.__match_img(templ_img)
        with allure.step(f'断言【{img_info}】存在'):
            allure.attach('断言', f'期望结果：大于{THRESHOLD}, 实际结果：{max_val}\n图片路径：{templ_img}')
            log.debug(f'实际匹配度：{max_val} - 图片路径：{templ_img}')
            if max_val <= THRESHOLD:
                self.savescreen('failures.png')
                log.info(f'期望结果：大于{THRESHOLD}, 实际结果：{max_val}\n图片路径：{templ_img}')
            assert max_val > THRESHOLD

        # 根据 x_percent 和 y_percent 系数，可以返回图像中或图像外的其他位置坐标
        if x_percent and y_percent:
            x = max_loc[0] + int(w * x_percent)
            y = max_loc[1] + int(h * y_percent)
            log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
            return int(x), int(y)
        if x_percent:
            x = max_loc[0] + int(w * x_percent)
            y = max_loc[1] * 2 + h
            log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
            return int(x), int(y / 2)
        if y_percent:
            x = max_loc[0] * 2 + w
            y = max_loc[1] + int(h * y_percent) if y_percent >= 0 else max_loc[1] - int(h * y_percent)
            log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
            return int(x / 2), int(y)

        # 根据宽高和左上角坐标计算中心点
        x = max_loc[0] * 2 + w
        y = max_loc[1] * 2 + h
        log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
        return int(x / 2), int(y / 2)

    def get_locs_position(self, img_info, templ_img, x_percent=None, y_percent=None):
        """ 获取多个匹配图像的坐标
        :param templ_img: 被查找图像路径
        :param x_percent: 横向百分比系数
        :param y_percent: 纵向百分比系数
        :return: 匹配图像中心坐标
        默认返回图像的中心坐标
        x_percent不为空时，返回 (横坐标*x_percent, y中心坐标) 处的坐标
        y_percent不为空时，返回 (x中心坐标，纵坐标*y_percent) 处的坐标
        x_percent 和 y_percent 都不为空时，返回 (横坐标*x_percent，纵坐标*y_percent) 坐标
        """
        h, w, ret = self.__match_imgs(templ_img)
        loc = np.where(ret >= THRESHOLD)
        if not loc:
            self.savescreen('failures.png')
            log.info('未找到合适坐标')
        assert loc

        pt_list = [(pt[1], pt[0]) for pt in zip(*loc)]
        max_locs = self.locs_same(pt_list)

        xy = []
        # 根据 x_percent 和 y_percent 系数，可以返回图像中或图像外的其他位置坐标
        for max_loc in max_locs:
            if x_percent and y_percent:
                x = max_loc[0] + int(w * x_percent)
                y = max_loc[1] + int(h * y_percent)
                log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
                xy.append((int(x), int(y)))

            elif x_percent:
                x = max_loc[0] + int(w * x_percent)
                y = max_loc[1] * 2 + h
                log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
                xy.append((int(x), int(y / 2)))

            elif y_percent:
                x = max_loc[0] * 2 + w
                y = max_loc[1] + int(h * y_percent)
                log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
                xy.append((int(x / 2), int(y)))
            else:
                # 根据宽高和左上角坐标计算中心点
                x = max_loc[0] * 2 + w
                y = max_loc[1] * 2 + h
                log.debug(f'图像正常匹配，返回坐标:({int(x)},{int(y)})')
                xy.append((int(x / 2), int(y / 2)))
        length = len(xy)
        with allure.step(f'断言【{img_info}】存在多个'):
            allure.attach('断言', f'期望结果：坐标不为空, 实际结果：坐标个数：{length}，坐标：{max_locs}\n图片路径：{templ_img}')
            log.info(f'找到坐标个数：{length}，坐标：{max_locs}')
            assert max_locs
        return length, xy

    @staticmethod
    def locs_same(loc1):
        """
        根据匹配结果的坐标间距进行去重
        :param loc1:
        :return:
        """
        count = len(loc1)
        threshold = 10  # 10个像素点以内则视为同一目标
        i = 0

        while (i < count):
            for j in range(count):
                if j != i:
                    if np.abs(loc1[j][0] - loc1[i][0]) <= threshold:  # x坐标
                        if np.abs(loc1[j][1] - loc1[i][1]) <= threshold:  # y坐标
                            loc1[j] = loc1[i]  # 近似坐标归一处理
            i += 1
        resl = sorted(set(loc1), key=lambda d: (d[0], d[1]))  # 去除归一后的多余结果，完成去重，并排序
        return resl


if __name__ == '__main__':
    OpenCV().savescreen('zz_screen.png')
