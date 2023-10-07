# -*- coding:utf-8 -*-
# @Time   : 2022/2/9 17:38
# @Author : tq
# @File   : robot.py
import requests

from conf.config import conf
from utils.log import log
from conf.config import conf


def send_info(info):
    """ 发送日志信息 """
    if not conf.is_ide:
        host = conf.host_ip
        vm_name = conf.vm_name
        all_url = host+'/send_info/'+vm_name+':'+info.replace("/", "-")
        try:
            resp = requests.get(all_url)
            if resp.json().get("code") == 0:
                log.info(f'成功发送请求get请求：{all_url}')
            else:
                log.error(f'成功发送请求，返回结果：{resp.json()}')
            return resp.json()
        except Exception as e:
            log.error(f'发送get请求失败.{e}{all_url}')
            return {}


def reports_robot(msg_info):
    # url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=52999afb-ee01-456c-9ba7-a0f1ae9cadf4'
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=52999afb-ee01-456c-9ba7-a0f1ae9cadf4'
    headers = {"Content-Type": "text/plain"}
    data = {
        "msgtype": "text",
        "text": {
            "content": msg_info,
        }
    }

    resp = requests.post(url=url, headers=headers, json=data)
    print(resp.text)


def create_snapshot(snapshot):
    """ 创建快照 """
    if not conf.is_ide:
        host = conf.host_ip
        vm_name = conf.vm_name
        url = host + '/create_snapshot'
        data = {'windows': vm_name, 'snapshot': snapshot}
        try:
            resp = requests.post(url, json=data)
            log.info(f'{resp.text}')
            send_info(f'{resp.text}')
            return resp.json()
        except Exception as e:
            log.error(f'create_snapshot接口请求出错:{e},url:{url},data:{data}')
            return {}


if __name__ == '__main__':
    reports_robot('此群完全是测试脚本用-任何人无需关心内容')