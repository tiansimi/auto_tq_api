# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 17:36
# @Author : tq
# @File   : report.py

import os
import json
import shutil
import platform
import allure
import pytest

from utils.robot import reports_robot
from conf.confpath import ConfPath
from conf.config import conf
from utils.log import log
from utils.file import fo
from utils.robot import send_info

# 系统信息报告命名文件夹名称
system_info = conf.vm_name
# 获取版本号
id2, version2 = fo.get_id_version(ConfPath.PATH_SRC)

# 远程报告路径
report_remote_dir = os.path.join(ConfPath.REPORT_REMOTE_DIR, system_info)
# 本地结果路径
result_loc_dir = ConfPath.RESULT_LOC_DIR
# 合并测试报告路径
html_url = os.path.join(ConfPath.REPORT_REMOTE_DIR, 'index.html')
html_model_url = os.path.join(ConfPath.REPORT_REMOTE_DIR, 'index_model.html')

# 历史记录
history = os.path.join(report_remote_dir, 'history')
history_trend_file = os.path.join(history, 'history-trend-copy.json')
duration_trend_file = os.path.join(history, 'duration-trend-copy.json')
retry_trend_file = os.path.join(history, 'retry-trend-copy.json')
categories_trend_file = os.path.join(history, 'categories-trend-copy.json')


def report_show(module_name, case_name, case_link='/'):
    """ 报告展示部分
    :param module_name: 二级模块名称
    :param case_name: 测试用例名称
    :param case_link: 测试用例链接
    :return:
    """
    # allure.dynamic.feature(module_name)
    allure.dynamic.story(module_name)
    allure.dynamic.title(case_name)
    allure.dynamic.tag(case_name)
    allure.dynamic.link(case_link, name='测试用例链接')


class Report:
    """ 把测试结果通过 allure 整合成测试报告 """
    def __init__(self):
        self.report_url = ConfPath.REPORT_REMOTE_URL + '/' + system_info
        if not os.path.exists(history):
            os.makedirs(history)

    def get_dirname(self):
        """ 获取历史测试报告文件夹名称 """
        old_datas = []
        try:
            # 首次进行生成报告，肯定会进到这一步，先创建 history-trend-copy.json 等备份文件夹
            if any((not os.path.exists(history_trend_file),
                    not os.path.exists(duration_trend_file),
                    not os.path.exists(retry_trend_file),
                    not os.path.exists(categories_trend_file))):
                with open(history_trend_file, 'w'): pass
                with open(duration_trend_file, 'w'): pass
                with open(retry_trend_file, 'w'): pass
                with open(categories_trend_file, 'w'): pass
                return 1, [None, None, None, None]  # 返回构建次数1（代表首次）
            else:
                with open(history_trend_file) as f: old_datas.append(json.load(f))
                with open(duration_trend_file) as f: old_datas.append(json.load(f))
                with open(retry_trend_file) as f: old_datas.append(json.load(f))
                with open(categories_trend_file) as f: old_datas.append(json.load(f))

                # 所有历史 根据构建次数进行排序，从大到小
                for old_data in old_datas:
                    old_data.sort(key=lambda x: x['buildOrder'], reverse=True)

                # 返回下一次的构建次数及历史数据
                return old_datas[0][0]["buildOrder"]+1, old_datas
        except Exception as e:
            log.error(f'获取历史文件夹名称出错：{e}')

    def update_trend_data(self, dirname: int, old_datas: list):
        """ 读取新报告，改造新报告，更新所有报告，备份历史报告数据
        dirname：构建次数
        old_datas：备份的数据
        """
        files_json = ['history-trend.json', 'duration-trend.json', 'retry-trend.json','categories-trend.json']
        files_copy_json = [history_trend_file, duration_trend_file, retry_trend_file, categories_trend_file]
        WIDGETS_DIR = os.path.join(report_remote_dir, '{}/widgets'.format(str(dirname)))

        for old_data, file_json, file_copy in zip(old_datas, files_json, files_copy_json):
            if os.path.exists(os.path.join(WIDGETS_DIR, file_json)):
                # 读取最新生成的history-trend.json数据
                with open(os.path.join(WIDGETS_DIR, file_json)) as f:
                    new_data = json.load(f)
                # --------------- 改造新报告 ---------------------#
                # 添加构建次数
                if old_data:
                    new_data[0]['buildOrder'] = old_data[0]['buildOrder']+1
                else:
                    old_data = []
                    new_data[0]['buildOrder'] = 1

                # 添加reportUrl：reportUrl要根据自己的实际情况更改
                # /ui_auto5.0/Windows-10-10.0.19041-SP0-64bit/html/4/index.html
                new_data[0]["reportUrl"] = f'{self.report_url}/{dirname}/index.html'
                old_data.insert(0, new_data[0])  # 把最新的数据，插入到备份数据列表首位

                # 更新所有生成报告中的历史数据。这样的话，点击历史趋势图就可以实现新老报告切换
                for i in range(1, dirname+1):
                    json_trend = os.path.join(report_remote_dir, '{}/widgets/{}'.format(str(i), file_json))
                    if os.path.exists(json_trend):
                        with open(os.path.join(report_remote_dir, '{}/widgets/{}'.format(str(i), file_json)), "w") as f:
                            json.dump(old_data, f)

                # 备份历史报告数据到 history 文件夹
                with open(file_copy, 'w') as f:
                    json.dump(old_data, f)
        url = f"{self.report_url}/{str(dirname)}/index.html"
        url_history = f"{self.report_url}/{str(dirname - 1)}/index.html"

        if dirname == 1:
            url_history = url
        return url, url_history

    def create_html(self):
        """
        生成 html 报告
        """
        try:
            # 调用 get_dirname()，获取到本次需要构建的次数
            buildOrder, old_datas = self.get_dirname()

            # 加入环境变量
            if os.path.exists(result_loc_dir):
                env = f'system_name={system_info}\n' \
                      f'version=center: {version2}\n' \
                      f'id=center: {id2}\n' \
                      f'python_version={platform.python_version()}'
                with open(os.path.join(result_loc_dir, 'environment.properties'), 'w', encoding='utf-8') as f:
                    f.write(env)

            # 生成 html 静态工程
            log.info('--------正在生成HTML报告，请稍后---------')
            try:
                cmd = f'allure generate {result_loc_dir} -o {os.path.join(report_remote_dir, str(buildOrder))} --clean'
                os.system(cmd)
            except Exception as e:
                log.error('生成HTML报告失败！错误信息：{}'.format(e))
                raise e

            # 更新备份历史数据 history
            try:
                url, url_history = self.update_trend_data(buildOrder, old_datas)
            except Exception as e:
                log.error('更新历史报告失败！错误信息：{}'.format(e))
                raise e
            return buildOrder, url, url_history

        except Exception as e:
            log.error(f'生成报告出错：{e}')

    def delete_trend(self, file_path, n):
        try:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r') as f:
                    his = json.load(f)
                del his[n:]
                with open(file_path, 'w') as f:
                    json.dump(his, f)
        except Exception as e:
            log.error(f'删除历史文件报错：{e}')

    def delete_html(self, total, n):
        """
        :param total 总报告数
        :param n: 保留最近几次历史记录
        保留 html 报告历史
        """
        try:
            for i in range(total - n):
                path = os.path.join(report_remote_dir, str(i + 1))
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                except Exception as e:
                    if os.path.isdir(path):
                        log.error(f'文件夹{path}，删除失败!\n失败原因：{e}')
        except Exception as e:
            log.error(f'删除以前测试报告出错：{e}')

    def get_total_count(self):
        """ 获取 本次运行结束后 用例数量 """
        try:
            cnt_file = os.path.join(ConfPath.REPORT_LOC_DIR, 'result.txt')
            if os.path.exists(cnt_file):
                with open(cnt_file, 'r') as f:
                    cnt = json.load(f)

                passed = cnt.get("passed")
                # selected = cnt.get("selected")
                failed = cnt.get("failed")
                error = cnt.get("error")
                skipped = cnt.get("skipped")
                total = passed + failed + error + skipped
                return f'总:{total}，成功:{passed}，失败:{failed}，错误:{error}，跳过:{skipped}'
            else:
                return '数量未收集到'
        except Exception as e:
            log.error(f'获取本次运行数量报错：{e}')

    def edit_report_collection(self, url, url_history):
        """ 修改 报告集合 """
        log.info(f'html路径：{html_url}')
        with open(html_url, 'r', encoding='UTF-8') as f, open("%s.bak" % html_url, "w", encoding='UTF-8') as f2:
            for line in f.readlines():
                if conf.vm_name in line:
                    log.info(f'line修改前：{line}')
                    line = line.replace(line, f'<tr>'
                                              f'<td>'
                                              f'<li>'
                                              f'<a href={url} target="_blank">{conf.vm_name}</a>'
                                              f'</li>'
                                              f'</td>'
                                              f'<td>【center: {id2}-{version2}】--【{self.get_total_count()}】'
                                              f'</td>'
                                              f'<td><a href={url_history} target="_blank">[历史报告]</a></td>'
                                              f'</tr>\n')
                    log.info(f'line修改后：{line}')
                f2.write(line)
        os.remove(html_url)
        os.rename("%s.bak" % html_url, html_url)

    def edit_report_model(self, url_history):
        """ 修改 报告集合 """
        try:
            with open(html_model_url, 'r', encoding='UTF-8') as f, open("%s.bak" % html_model_url, "w", encoding='UTF-8') as f2:
                for line in f.readlines():
                    if conf.vm_name in line:
                        log.info('line修改前：{}'.format(line))
                        '''<tr><td><li><a href="/" target="_blank">test_automated_win7_sp1_x64_ultimate</a></li></td>
                        <td>【暂未生成报告】</td></tr>
                        '''
                        line = line.replace(line,
                                            f'<tr>'
                                            f'<td><li><a href="/" target="_blank">{conf.vm_name}</a></li></td>'
                                            f'<td>【暂未生成报告】</td>'
                                            f'<td><a href={url_history} target="_blank">[历史报告]</a></td></tr>\n')
                        log.info('line修改后：{}'.format(line))
                    f2.write(line)
            os.remove(html_model_url)
            os.rename("%s.bak" % html_model_url, html_model_url)
        except Exception as e:
            log.error('修改报告模板列表错误：{}'.format(e))

    def run(self, args, upload=False, send=False):
        """
        运行pytest主函数，并生成allure测试报告
        args: pytest运行参数
        :param args:
        :param upload: True 生成测试报告
        :param send: True 发送到微信群
        :return:
        """
        n = 5  # 保留多少条报告记录
        pytest.main(args)

        if upload or send:
            total, url, url_history = self.create_html()  # 生成html报告，包含历史曲线
            print(total, url)

            self.delete_html(total, n)
            self.delete_trend(history_trend_file, n)
            self.delete_trend(duration_trend_file, n)
            self.delete_trend(retry_trend_file, n)
            self.delete_trend(categories_trend_file, n)

            log.info('--------成功生成HTML报告---------')
            log.info(f'测试报告地址为：{url}')
            send_info(f'测试报告地址为：{url}')

            # 修改\\192.168.3.194中report_collection的文件
            self.edit_report_collection(url, url_history)
            self.edit_report_model(url)
            if send:
                # 群机器人发送测试报告到指定群
                reports_robot(
                    f'企业版2.0_api:【center: {id2}-{version2}】--【{self.get_total_count()}】\n'
                    f'系统：{system_info}\n'
                    f'接口自动化测试报告：\n'
                    f'{ConfPath.REPORT_REMOTE_URL + "/index.html"}')


if __name__ == '__main__':
    # pass
    Report().get_total_count()

