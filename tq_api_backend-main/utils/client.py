# -*- coding:utf-8 -*-
# @Time   : 2022/4/28 11:23
# @Author : tq
# @File   : client.py
import allure
import time
from threading import Thread, Event
from dictdiffer import diff
from apis.api_client import ApiClient
from apis.data_client import DataClient
from apis.endpoints_manage.api_endpoints import ApiEndpoints
from apis.endpoints_manage.data_endpoints import DataEndpoints
from conf.confpath import ConfParams
from conf.config import conf
from utils.functions import random_int
from utils.log import log
from jsonpath import jsonpath

finished = Event()


class ClientThread(Thread):
    def __init__(self, cid):
        Thread.__init__(self)
        self.client = ApiClient()
        self.center = ApiEndpoints()
        self.cid = cid
        self.token = ''
        self.interval = int(conf.time_heart_beet)
        self.client_name = f'a0Dell-DCF1M53{random_int(0, 100)}'

    def send_preonline(self):
        resp = self.client.client_pre_online(self.cid, data=DataClient.data_preonline(self.cid))
        if resp.get('errno') == 0:
            self.token = jsonpath(resp, '$..token')[0]
        else:
            raise ValueError(f'预上线返回失败:{resp}')

    def send_confirm(self):
        heart_confirm = DataClient.data_confirm(self.token, self.cid, self.client_name)
        resp = self.client.client_confirm(self.cid, data=heart_confirm)
        if resp.get('errno') == 0:
            ConfParams.HEART_CONFIRM = heart_confirm
            return resp

    def send_online(self):
        resp = self.client.client_online(self.cid, data=DataClient.data_online(self.cid, self.client_name))
        if resp.get('errno') == 0:
            return resp

    def send_heart_beet_first(self, include_asset=False):
        heart_beet_first = DataClient.data_heart_beet_first(include_asset)
        resp = self.client.client_heart_beet_first(self.cid, data=heart_beet_first)
        if resp.get('errno') == 0:
            ConfParams.HEART_BEET_OLD = resp
            ConfParams.HEART_BEET_FIRST = heart_beet_first
            finished.set()
        else:
            raise ValueError(f'返回结果错误：{resp}')

    def send_heart_beet_second(self, info, detail=False):
        """ 发送心跳
        :return: 没有任务返回 空列表，否则：[('change', 'data.task_ts', (1651211109, 1651125413))]
        """
        if detail == 'users':
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second_users)
        elif detail == 'swinfo':
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second_swinfo)
        else:
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second)
        if resp.get('errno') == 0:
            ConfParams.HEART_BEET_NEW = resp
            log.info(f'子线程：{finished.is_set()}--{self.cid}/_heartbeat')
            finished.set()
            with allure.step(f'记录心跳前后返回值'):
                allure.attach('心跳前后', f'前一个心跳返回值：{ConfParams.HEART_BEET_OLD}\n'
                                      f'本次心跳返回值：{ConfParams.HEART_BEET_NEW}')
                print(f'前一个心跳返回值：{ConfParams.HEART_BEET_OLD}\n本次心跳返回值：{ConfParams.HEART_BEET_NEW}')
                dif_result = list(diff(ConfParams.HEART_BEET_NEW, ConfParams.HEART_BEET_OLD))
                if dif_result:
                    log.info(f'心跳变化字段详细：{dif_result}')
                    ConfParams.HEART_BEET_OLD = ConfParams.HEART_BEET_NEW

                dif_list = []
                for dif in dif_result:
                    if dif[0] == 'remove':
                        for data in dif[2]:
                            dif_list.append(dif[1] + '.' + data[0])
                    else:
                        dif_list.append(dif[1])
                return dif_list
        else:
            log.error(f'二次心跳返回错误：{resp}')
            # raise ValueError(f'返回结果错误：{resp}')

    def send_sync(self, info):
        """ 心跳和上次不一样时，同步任务 """
        return self.client.client_sync(info, self.cid)

    def send_task_report3(self, info, task_id):
        """ 上报任务状态(等待执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 3))

    def send_task_report1(self, info, task_id):
        """ 上报任务状态(正在执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 1))

    def send_task_report2_completed(self, info, task_id):
        """ 上报任务状态(执行完成) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 2, message='completed'))

    def send_task_report2_refused(self, info, task_id):
        """ 上报任务状态(拒绝执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 2, message='refused'))

    def get_client_stat(self):
        resp = self.center.center_clnt_query(f'中心 - 终端列表查询（单独线程）', DataEndpoints.data_clnt_query)
        try:
            stat = jsonpath(resp, f'$..list[?(@.cid=="{self.cid}")].stat')[0]
            if stat == 2:  # stat 离线：1  在线：2   异常：3
                return True
            return False
        except:
            return False

    def run(self):
        """ 终端模拟 只发生一次心跳 """
        if not self.get_client_stat():
            self.send_preonline()
            self.send_confirm()
            time.sleep(1.5)
            self.send_heart_beet_first()
        else:
            self.send_heart_beet_second('发送第二次心跳（单独线程）')

        while True:
            finished.clear()
            for i in range(self.interval):
                finished.wait(1)
                if finished.isSet():
                    break
            if not finished.isSet():
                try:
                    self.send_heart_beet_second('发送第二次心跳（单独线程）')
                except:
                    self.send_heart_beet_second('重新发送第二次心跳（单独线程）')


class Client:

    def __init__(self, cid):
        self.client = ApiClient()
        self.center = ApiEndpoints()
        self.cid = cid
        self.token = ''
        self.client_name = f'a0Dell-DCF1M53{random_int(0, 100)}'

    def send_preonline(self):
        resp = self.client.client_pre_online(self.cid, data=DataClient.data_preonline(self.cid))
        if resp.get('errno') == 0:
            self.token = jsonpath(resp, '$..token')[0]
        else:
            raise ValueError(f'预上线返回失败:{resp}')

    def send_confirm(self):
        heart_confirm = DataClient.data_confirm(self.token, self.cid, self.client_name)
        resp = self.client.client_confirm(self.cid, data=heart_confirm)
        if resp.get('errno') == 0:
            ConfParams.HEART_CONFIRM = heart_confirm
            return resp

    def send_online(self):
        resp = self.client.client_online(self.cid, data=DataClient.data_online(self.cid, self.client_name))
        if resp.get('errno') == 0:
            return resp

    def send_heart_beet_first(self, include_asset=False):
        heart_beet_first = DataClient.data_heart_beet_first(include_asset=include_asset)
        resp = self.client.client_heart_beet_first(self.cid, data=heart_beet_first)
        if resp.get('errno') == 0:
            ConfParams.HEART_BEET_OLD = resp
            ConfParams.HEART_BEET_FIRST = heart_beet_first
            finished.set()
        else:
            raise ValueError(f'返回结果错误：{resp}')

    def send_heart_beet_second(self, info, detail=False):
        """ 发送心跳
        :return: 没有任务返回 空列表，否则：[('change', 'data.task_ts', (1651211109, 1651125413))]
        """
        if detail == 'users':
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second_users)
        elif detail == 'swinfo':
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second_swinfo)
        elif detail == 'malfunction':
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second_malfunction)
        else:
            resp = self.client.client_heart_beet_second(info, self.cid, data=DataClient.data_heart_beet_second)
        if resp.get('errno') == 0:
            ConfParams.HEART_BEET_NEW = resp
            log.info(f'主线程：{finished.is_set()}--{self.cid}/_heartbeat')
            finished.set()

            with allure.step(f'记录心跳前后返回值'):
                allure.attach('心跳前后', f'前一个心跳返回值：{ConfParams.HEART_BEET_OLD}\n'
                                      f'本次心跳返回值：{ConfParams.HEART_BEET_NEW}')
                print(f'前一个心跳返回值：{ConfParams.HEART_BEET_OLD}\n本次心跳返回值：{ConfParams.HEART_BEET_NEW}')
                dif_result = list(diff(ConfParams.HEART_BEET_NEW, ConfParams.HEART_BEET_OLD))
                if dif_result:
                    log.info(f'心跳变化字段详细：{dif_result}')
                    ConfParams.HEART_BEET_OLD = ConfParams.HEART_BEET_NEW
                dif_list = []
                for dif in dif_result:
                    if dif[0] == 'remove':
                        for data in dif[2]:
                            dif_list.append(dif[1] + '.' + data[0])
                    else:
                        dif_list.append(dif[1])
                return dif_list
        else:
            raise ValueError(f'返回结果错误：{resp}')

    def send_sync(self, info):
        """ 心跳和上次不一样时，同步任务 """
        return self.client.client_sync(info, self.cid)

    def send_task_report3(self, info, task_id):
        """ 上报任务状态(等待执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 3))

    def send_task_report1(self, info, task_id):
        """ 上报任务状态(正在执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 1))

    def send_task_report2_completed(self, info, task_id):
        """ 上报任务状态(执行完成) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 2, message='completed'))

    def send_task_report2_refused(self, info, task_id):
        """ 上报任务状态(拒绝执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 2, message='refused'))

    def get_client_stat(self):
        resp = self.center.center_clnt_query(f'中心 - 终端列表查询', DataEndpoints.data_clnt_query)
        try:
            stat = jsonpath(resp, f'$..list[?(@.cid=="{self.cid}")].stat')[0]
            if stat == 2:  # stat 离线：1  在线：2   异常：3
                return True
            return False
        except:
            return False

    def online(self, include_asset=False):
        """ 终端模拟 只发生一次心跳 """
        if not self.get_client_stat():
            self.send_preonline()
            self.send_confirm()
            time.sleep(1.5)
            self.send_heart_beet_first(include_asset)
        else:
            self.send_heart_beet_second('发送第二次心跳')


if __name__ == '__main__':
    c = Client('4FF902ECDBFD17071147C85C14E48D5600000000')
    # c.start()

    # {'errno': 0, 'data': {'client_id': '57012416FAA6968A5CD0AC316289810600000001', 'server_id': 'WqVIZJFFQYMkEWqV', 'interval': 30, 'service_tag': 'BJ04098742', 'token': 'd0f1e12145fcee553d2b8bb38eab7cc7'}}
    # Client('57012416FAA6968A5CD0AC316289810600000000').send_heart_beet()
