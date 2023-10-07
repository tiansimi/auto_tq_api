# -*- coding:utf-8 -*-
# @Time   : 2022/2/10 14:57
# @Author : tq
# @File   : base_api.py
import os
import time
import random
import json
import zlib

import requests
import allure
from conf.config import Config
from conf.confpath import ConfParams
from utils.log import log

conf = Config()


class BaseApi:

    def __init__(self):
        self.center_url = conf.center_url
        self.client_url = conf.client_url
        self.sc_center_url = conf.sc_center_url
        self.sc_client_url = conf.sc_client_url

    def http_client(self, step_info, data, body=True, not_download=True):
        """
        终端请求数据
        :param step_info:
        :param data: 通用请求格式，参考 api 封装
        :param body: 是否返回 body 信息
        :return:
        """
        if not 'url' in data:
            raise ValueError('请求参数中没有 url')
        if not data['url'].startswith('http'):
            data['url'] = self.client_url + data['url']
        data_src = data

        # log.info(f'{step_info}-client请求数据：{json.dumps(data_src, ensure_ascii=False, sort_keys=True)}')
        log.info(f'{step_info}-client请求数据：{str(data_src)}')
        if 'data' in data:
            data['data'] = zlib.compress(data['data'].encode(encoding='UTF-8'), 6)

        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}-client请求数据', str(data_src))
            try:
                requests.DEFAULT_RETRIES = 5
                resp = requests.request(**data)
                if not_download:
                    if body:
                        try:
                            js = resp.json()
                            log.info(f'{step_info}-client返回结果：{json.dumps(js, ensure_ascii=False, sort_keys=True)}')
                            allure.attach('client返回结果', json.dumps(js, ensure_ascii=False, sort_keys=True, indent=2))
                            # assert js.get('errno') == 0
                            return js
                        except:
                            txt = resp.text
                            allure.attach('client返回结果', txt)
                            log.error(txt)
                            return resp.text
                    else:
                        return resp
                else:
                    return resp.status_code
            except Exception as e:
                log.error(f'请求响应出错！出错信息为：{e}')
                allure.attach('响应出错信息', f'请求响应出错！出错信息为：{e}')

    def http_center(self, step_info, data, body=True, iserrno=True, html=False, **kwargs):
        """
        中心接口请求调用
        :param step_info: 步骤信息
        :param data: 请求参数字典
        :param body: 是否返回body（只返回json时参数有效）
        :param iserrno 是否显示错误值
        :param html: 是否返回其他格式对象
        :return:
        """
        time.sleep(random.random())
        if isinstance(data, str):
            data = json.loads(self.replace_str(data))
        if not isinstance(data, dict):
            raise ValueError(f'data数据不是正确的字典格式，请检查传入参数！\n当前data 为: {data}')
        if not 'url' in data:
            raise ValueError('请求参数中没有 url')
        if not data['url'].startswith('http'):
            data['url'] = self.center_url + data['url']
        # 请求加入 headers 和 cookies
        data['headers'], data['cookies'] = {}, {}
        data['headers'] = ConfParams.HEADERS
        data['cookies'] = ConfParams.COOKIES
        if kwargs:
            for kw in kwargs:
                data['headers'][kw] = kwargs[kw]

        log.info(f'{step_info}-center请求数据：{str(data)}')
        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}-center请求数据', str(data))
            try:
                resp = requests.request(**data)
                if not html:
                    try:
                        resp.json()
                        if iserrno:
                            assert resp.json().get('errno') == 0
                    except Exception as e:
                        log.error(f'返回值错误：{e}{resp.text}')
                        assert 0
                else:
                    body = False
                    resp.encoding = 'utf-8'
                    return resp.text
                # 更新 cookies
                if resp.cookies.get('HRESSCSRF'):
                    ConfParams.HEADERS['HTTP-CSRF-TOKEN'] = resp.cookies.get('HRESSCSRF')
                    ConfParams.COOKIES['HRESSCSRF'] = resp.cookies.get('HRESSCSRF')
                if body:
                    try:
                        log.debug(resp.text)
                        js = resp.json()
                        allure.attach(f'{step_info}-center返回结果',
                                      json.dumps(js, ensure_ascii=False, sort_keys=True, indent=4))
                        log.info(f'{step_info}-center返回结果:{json.dumps(js, ensure_ascii=False, sort_keys=True)}')
                        return js
                    except Exception as e:
                        log.error(f'错误：{e}')
                        txt = resp.text
                        log.error(txt)
                        allure.attach(f'{step_info}-center返回结果', txt)
                        return txt
                else:
                    return resp
            except Exception as e:
                log.error(f'center请求响应出错！出错信息为：{e}')
                allure.attach('center请求响应出错', f'请求响应出错！出错信息为：{e}')

    def http_multistage_center(self, step_info, data, iserrno=True, body=True, html=False, **kwargs):
        """
        多级中心 - 上级中心验证接口
        :param step_info: 步骤信息
        :param data: 请求参数字典
        :param iserrno: 是否断言errno是否为0
        :param body: 是否返回body（只返回json时参数有效）
        :param html: 是否返回其他格式对象
        :return:
        """
        time.sleep(random.random())
        if isinstance(data, str):
            data = json.loads(self.replace_str(data))
        if not isinstance(data, dict):
            raise ValueError(f'data数据不是正确的字典格式，请检查传入参数！\n当前data 为: {data}')
        if not 'url' in data:
            raise ValueError('请求参数中没有 url')
        if not data['url'].startswith('http'):
            data['url'] = self.sc_center_url + data['url']
        # 请求加入 headers 和 cookies
        data['headers'], data['cookies'] = {}, {}
        data['headers'] = ConfParams.SC_HEADERS
        data['cookies'] = ConfParams.SC_COOKIES
        if kwargs:
            for kw in kwargs:
                data['headers'][kw] = kwargs[kw]

        log.info(f'{step_info}-center请求数据：{str(data)}')
        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}-center请求数据', str(data))
            try:
                resp = requests.request(**data)
                if not html:
                    try:
                        resp.json()
                        if iserrno:
                            assert resp.json().get('errno') == 0
                    except Exception as e:
                        log.error(f'返回值错误：{e}{resp.text}')
                        assert 0
                else:
                    body = False
                    resp.encoding = 'utf-8'
                # 更新 cookies
                if resp.cookies.get('HRESSCSRF'):
                    ConfParams.HEADERS['HTTP-CSRF-TOKEN'] = resp.cookies.get('HRESSCSRF')
                    ConfParams.COOKIES['HRESSCSRF'] = resp.cookies.get('HRESSCSRF')
                if body:
                    try:
                        log.debug(resp.text)
                        js = resp.json()
                        allure.attach(f'{step_info}-center返回结果',
                                      json.dumps(js, ensure_ascii=False, sort_keys=True, indent=4))
                        log.info(f'{step_info}-center返回结果:{json.dumps(js, ensure_ascii=False, sort_keys=True)}')
                        return js
                    except Exception as e:
                        log.error(f'错误：{e}')
                        txt = resp.text
                        log.error(txt)
                        allure.attach(f'{step_info}-center返回结果', txt)
                        return txt
                else:
                    return resp
            except Exception as e:
                log.error(f'center请求响应出错！出错信息为：{e}')
                allure.attach('center请求响应出错', f'请求响应出错！出错信息为：{e}')

    def http_multistage_lower_center(self, step_info, data, url, iserrno=True, body=True, html=False, **kwargs):
        """
        多级中心 - 上级中心验证接口
        :param step_info: 步骤信息
        :param data: 请求参数字典
        :param url: 请求的 url
        :param iserrno: 是否断言errno是否为0
        :param body: 是否返回body（只返回json时参数有效）
        :param html: 是否返回其他格式对象
        :return:
        """
        time.sleep(random.random())
        if isinstance(data, str):
            data = json.loads(self.replace_str(data))
        if not isinstance(data, dict):
            raise ValueError(f'data数据不是正确的字典格式，请检查传入参数！\n当前data 为: {data}')
        if not 'url' in data:
            raise ValueError('请求参数中没有 url')
        if not data['url'].startswith('http'):
            data['url'] = url + data['url']
        # 请求加入 headers 和 cookies
        data['headers'], data['cookies'] = {}, {}
        # data['headers'] = ConfParams.SC_HEADERS
        # data['cookies'] = ConfParams.SC_COOKIES
        if kwargs:
            for kw in kwargs:
                data['headers'][kw] = kwargs[kw]

        log.info(f'{step_info}-center请求数据：{str(data)}')
        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}-center请求数据', str(data))
            try:
                resp = requests.request(**data)
                if not html:
                    try:
                        resp.json()
                        if iserrno:
                            assert resp.json().get('errno') == 0
                    except Exception as e:
                        log.error(f'返回值错误：{e}{resp.text}')
                        assert 0
                else:
                    body = False
                    resp.encoding = 'utf-8'
                # 更新 cookies
                # if resp.cookies.get('HRESSCSRF'):
                #     ConfParams.HEADERS['HTTP-CSRF-TOKEN'] = resp.cookies.get('HRESSCSRF')
                #     ConfParams.COOKIES['HRESSCSRF'] = resp.cookies.get('HRESSCSRF')
                if body:
                    try:
                        log.debug(resp.text)
                        js = resp.json()
                        allure.attach(f'{step_info}-center返回结果',
                                      json.dumps(js, ensure_ascii=False, sort_keys=True, indent=4))
                        log.info(f'{step_info}-center返回结果:{json.dumps(js, ensure_ascii=False, sort_keys=True)}')
                        return js
                    except Exception as e:
                        log.error(f'错误：{e}')
                        txt = resp.text
                        log.error(txt)
                        allure.attach(f'{step_info}-center返回结果', txt)
                        return txt
                else:
                    return resp
            except Exception as e:
                log.error(f'center请求响应出错！出错信息为：{e}')
                allure.attach('center请求响应出错', f'请求响应出错！出错信息为：{e}')

    def http_multistage_client(self, step_info, data, body=True):
        """
        终端请求数据 - 多级中心
        :param step_info:
        :param data: 通用请求格式，参考 api 封装
        :param body: 是否返回 body 信息
        :return:
        """
        if not 'url' in data:
            raise ValueError('请求参数中没有 url')
        if not data['url'].startswith('http'):
            data['url'] = self.sc_client_url + data['url']
        data_src = data

        # log.info(f'{step_info}-client请求数据：{json.dumps(data_src, ensure_ascii=False, sort_keys=True)}')
        if 'data' in data:
            data['data'] = zlib.compress(data['data'].encode(encoding='UTF-8'), 6)

        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}-client请求数据', str(data_src))
            try:
                resp = requests.request(**data)
                if body:
                    try:
                        js = resp.json()
                        log.info(f'{step_info}-client返回结果：{json.dumps(js, ensure_ascii=False, sort_keys=True)}')
                        allure.attach('client返回结果', json.dumps(js, ensure_ascii=False, sort_keys=True, indent=2))
                        # assert js.get('errno') == 0
                        return js
                    except:
                        txt = resp.text
                        allure.attach('client返回结果', txt)
                        log.error(txt)
                        return resp.text
                else:
                    return resp
            except Exception as e:
                log.error(f'请求响应出错！出错信息为：{e}')
                allure.attach('响应出错信息', f'请求响应出错！出错信息为：{e}')

    def http_center_download_files(self, step_info, data, file_path=None, **kwargs):
        """
        中心接口请求调用 - 文件下载
        :param step_info: 步骤信息
        :param data: 请求参数字典
        :param file_path: 文件存储本地地址  D:/response.xlsx
        :param html: 是否返回其他格式对象
        :return:
        """
        time.sleep(random.random())
        if isinstance(data, str):
            data = json.loads(self.replace_str(data))
        if not isinstance(data, dict):
            raise ValueError(f'data数据不是正确的字典格式，请检查传入参数！\n当前data 为: {data}')
        if not 'url' in data:
            raise ValueError('请求参数中没有 url')
        if not data['url'].startswith('http'):
            data['url'] = self.center_url + data['url']
        # 请求加入 headers 和 cookies
        data['headers'], data['cookies'] = {}, {}
        data['headers'] = ConfParams.HEADERS
        data['cookies'] = ConfParams.COOKIES
        if kwargs:
            for kw in kwargs:
                data['headers'][kw] = kwargs[kw]

        log.info(f'{step_info}-center请求数据：{str(data)}')
        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}-center请求数据', str(data))
            try:
                # url = 'http://127.0.0.1:8080/mgr/log/log_export/_dow?id=25&_=1662628304068'
                # resp = requests.get(url, cookies=data['cookies'], headers=data['headers'])
                resp = requests.get(**data)
                if resp.status_code == 200:
                    if not os.path.isdir(file_path):
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, "wb") as f:
                        f.write(resp.content)
                    return resp
                else:
                    log.error(f'错误：文件下载失败，状态码：{resp.status_code}')
                    txt = resp.text
                    allure.attach(f'{step_info}-center返回结果', txt)
                    return txt
            except Exception as e:
                log.error(f'center请求响应出错！出错信息为：{e}')
                allure.attach('center请求响应出错', f'请求响应出错！出错信息为：{e}')
                assert 0

    @staticmethod
    def replace_str(data):
        """
        字符替换
        :param data:
        :return:
        """
        if isinstance(data, str):
            new_data = data \
                .replace('｛', '{').replace('｝', '}') \
                .replace('‘', '"').replace('”', '"') \
                .replace("\'", '"')

            return new_data
        return data

    @staticmethod
    def wait_time(tm):
        """ 等待时间 """
        with allure.step(f'强行等待{tm}秒'):
            log.info(f'强行等待{tm}秒')
            time.sleep(tm)

    @staticmethod
    def center_service_wait_start(timeout):
        """ 等待中心服务启动 """
        end_time = time.time() + timeout
        while True:
            try:
                resp = requests.get(f'{conf.center_url}/auth/_login')
            except Exception as e:
                log.info(f'请求地址：get-{conf.center_url}/auth/_login')
                log.info(e)
                continue
            else:
                log.info(f'请求地址：get-{conf.center_url}/auth/_login')
                log.info(resp.text)
                if '"errno":-1' in resp.text:
                    break
            if time.time() > end_time:
                log.error(f'请求地址失败：get-{conf.center_url}/auth/_login')
                break
            time.sleep(2)


if __name__ == '__main__':
    import time

    re_api = BaseApi()
    # data = {
    #     'method': 'post',
    #     'url': '/auth/_login',
    #     'json': eval(conf.user_info)
    # }
    # resp = re_api.http_center('', data, body=True)
    # requests.request(**data)
    # ConfParams.HEADERS = {
    #     'HTTP-CSRF-TOKEN': resp.cookies.get('HRESSCSRF'),
    #     'Origin': conf.center_url
    # }
    # ConfParams.COOKIES = dict(resp.cookies)
    #
    # data1 = {
    #     'method': 'get',
    #     'url': '/mgr/group/_list',
    # }
    # resp = re_api.request_http(data1)
    # print(resp)
    # time.sleep(1)
    # data2 = {
    #     'method': 'post',
    #     'url': '/mgr/blacklist/_query',
    #     'json': {"view": {"begin": 0, "count": 15}, "order": {"tm": "desc"}}
    # }
    # resp = re_api.request_http(data2)
    # print(resp)
    # time.sleep(1)
    # data3 = {
    #     'method': 'post',
    #     'url': '/mgr/clnt_tag/_query',
    #     'json': {"view": {"begin": 0, "count": 15}, "order": {"name": "asc"}}
    # }
    # resp = re_api.request_http(data3)
    # print(resp)
    # time.sleep(1)
    # 修改密码
    reset_data = {
        'method': 'post',
        'url': 'http://192.168.3.70:8080/auth/_reset',
        'json': {"pwd": "admin", "newpwd": "585004c128942a72dae745732429b88d776d88f5"}
    }
    re_api.http_center('重置密码', reset_data)
