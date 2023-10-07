# -*- coding:utf-8 -*-
# @Time   : 2022/11/25 19:56
# @Author : tq
# @File   : api_others.py
"""
企业版2.0—中心  API接口认证机制 封装测试
"""

import time
import json
import base64
import hashlib
import hmac

import allure
import requests

from conf.config import conf
from utils.log import log


class ApiOthers:

    def get_author(self, method, url, secret_id, secret_key, data=''):
        """
        headers 中 Authorization字段计算的方法
        :param method: 请求方法
        :param url: 请求 url
        :param secret_id: API 接口 新增加的 Secret ID
        :param secret_key: API 接口 新增加的 Secret Key
        :param data: post 请求体
        :return: 签名信息 Authorization = "HRESS " + AccessKeyId + ":" + Expires + ":" + Signature
        """
        expires = int(time.time() * 1000) + 864000000  # 过期时间 当前时间 + 100天

        MD5 = hashlib.md5(data.encode()).digest()  # MD5
        content_MD5 = base64.b64encode(MD5).decode()  # base64加密

        canonicalizedResource = url[1:]  # 资源路径

        sign = f'{secret_id}\n{expires}\n{method.upper()}\n{content_MD5}\n{canonicalizedResource}'
        hmac_sign = hmac.new(secret_key.encode(), sign.encode(), hashlib.sha1).digest()  # hmac sha1值
        Signature = base64.b64encode(hmac_sign).decode()  # base64 编码成字符串
        Authorization = f'HRESS{secret_id}:{expires}:{Signature}'

        return Authorization

    # def http_other(self,step_info, method, url, secret_id, secret_key, data='', host_url=None):
    #     """
    #     第三方 请求接口
    #     :param method: 请求方法
    #     :param host_url: 请求地址
    #     :param url: 请求 url
    #     :param secret_id: API 接口 新增加的 Secret ID
    #     :param secret_key: API 接口 新增加的 Secret Key
    #     :param data: post 请求体
    #     :return: 响应数据
    #     """
    #     data = data.replace("\'", '\"')
    #     js_data = json.loads(data) if data else None
    #     if host_url is None:
    #         host_url = conf.center_url
    #     Authorization = self.get_author(method, url, secret_id, secret_key, data=data)
    #     headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': Authorization}
    #     try:
    #         rep = requests.request(method, host_url + url, json=js_data, headers=headers)
    #     except Exception as e:
    #         print(f'请求错误：{e}')
    #     else:
    #         return rep.json()
    def http_other(self, step_info, method, url, secret_id, secret_key, data='', host_url=None):
        """
        第三方 请求接口
        :param method: 请求方法
        :param url: 请求 url
        :param secret_id: API 接口 新增加的 Secret ID
        :param secret_key: API 接口 新增加的 Secret Key
        :param data: post 请求体
        :return: 响应数据
        :param host_url: 请求地址
        """
        data = data.replace("\'", '\"')
        js_data = json.loads(data) if data else None
        if host_url is None:
            host_url = conf.center_url
        Authorization = self.get_author(method, url, secret_id, secret_key, data=data)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': Authorization}
        log.info(f'{step_info}--请求数据 url：{host_url}，data：{str(js_data)}')
        with allure.step(f'{step_info}'):
            allure.attach(f'{step_info}--请求数据 url：{host_url}，data：', str(js_data))
            try:
                rep = requests.request(method, host_url + url, json=js_data, headers=headers)
            except Exception as e:
                # allure.attach('接口异常', e)
                log.error(e)
                print(f'请求错误：{e}')
            else:
                log.info(f'{step_info}-返回结果：{str(rep.json())}')
                allure.attach('返回结果', str(rep.json()))
                return rep.json()


if __name__ == '__main__':
    host_url = 'http://192.168.4.8:8080'
    req = ApiOthers()
    # 删除分组(带参数)
    method, url = 'post', '/api/group/_delete'
    secret_id, secret_key = 'WAIK335XL4', 'XAH64VU4C33QAI3WYXLM'
    data = {"group_id": 6}
    rep = req.http_other(method, url, secret_id, secret_key, data=str(data))
    print(rep)

    # 查询分组（不带参数）
    method, url = 'post', '/api/group/_list'
    secret_id, secret_key = 'WAIK335XL4', 'XAH64VU4C33QAI3WYXLM'
    rep = req.http_other(method, url, secret_id, secret_key)
    print(rep)
