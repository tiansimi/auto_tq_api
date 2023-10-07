import time
from threading import Thread

import allure
from dictdiffer import diff
from jsonpath import jsonpath

from apis.api_client_linux_mac import ApiClientLinuxMac
from apis.data_client import DataClient
from apis.data_client_linux import DataClientLinux
from conf.confpath import ConfParams
from utils.log import log


class ClientLinux(Thread):
    def __init__(self, cid):
        Thread.__init__(self)
        self.client = ApiClientLinuxMac()
        self.cid = cid
        self.token = ''
        self.product = DataClientLinux.data_api_product

    def send_preonline(self):
        """ 预上线 """
        resp = self.client.client_pre_online(self.cid, data=DataClientLinux.data_preonline(self.cid),
                                             product=self.product)
        if resp.get('errno') == 0:
            self.token = jsonpath(resp, '$..token')[0]
        else:
            raise ValueError(f'预上线返回失败:{resp}')

    def send_confirm(self):
        """ 上线确认 """
        resp = self.client.client_confirm(self.cid, data=DataClientLinux.data_confirm(self.token, 'test-Linux'),
                                          product=self.product)
        if resp.get('errno') == 0:
            return resp

    def send_heart_beet_first(self):
        """ 第一次心跳 """
        resp = self.client.client_heart_beet_first(self.cid, data=DataClientLinux.data_heart_beet_first,
                                                   product=self.product)
        if resp.get('errno') == 0:
            ConfParams.HEART_BEET_OLD = resp
        else:
            raise ValueError(f'返回结果错误：{resp}')

    def send_heart_beet_second(self, info):
        """ 发送心跳
        :return: 没有任务返回 空列表，否则：[('change', 'data.task_ts', (1651211109, 1651125413))]
        """
        resp = self.client.client_heart_beet_second(info, self.cid, data=DataClientLinux.data_heart_beet_second,
                                                    product=self.product)
        if resp.get('errno') == 0:
            ConfParams.HEART_BEET_NEW = resp
            with allure.step(f'记录心跳前后返回值'):
                allure.attach('心跳前后', f'前一个心跳返回值：{ConfParams.HEART_BEET_OLD}\n'
                                      f'本次心跳返回值：{ConfParams.HEART_BEET_NEW}')
                print(f'前一个心跳返回值：{ConfParams.HEART_BEET_OLD}\n本次心跳返回值：{ConfParams.HEART_BEET_NEW}')
                dif = list(diff(ConfParams.HEART_BEET_NEW, ConfParams.HEART_BEET_OLD))
                if dif:
                    log.info(f'心跳变化字段详细：{dif}')
                    ConfParams.HEART_BEET_OLD = ConfParams.HEART_BEET_NEW
                return [l[1] for l in dif]
        else:
            raise ValueError(f'返回结果错误：{resp}')

    def send_sync(self, info):
        """ 同步任务 """
        return self.client.client_sync(info, self.cid, product=self.product)

    def send_task_report3(self, info, task_id):
        """ 上报任务状态(等待执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 3), product=self.product)

    def send_task_report1(self, info, task_id):
        """ 上报任务状态(正在执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 1), product=self.product)

    def send_task_report2_completed(self, info, task_id):
        """ 上报任务状态(执行完成) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 2, message='completed'),
                                       product=self.product)

    def send_task_report2_refused(self, info, task_id):
        """ 上报任务状态(拒绝执行) """
        self.client.client_task_report(info, self.cid, DataClient.data_task_report(task_id, 2, message='refused'),
                                       product=self.product)

    def run(self):
        """ 终端模拟 只发生一次心跳 """
        try:
            self.send_preonline()
            self.send_confirm()
            time.sleep(1.5)
            self.send_heart_beet_first()
            self.send_sync('第一次同步配置')
        except:
            self.send_heart_beet_second('发送第二次心跳')
            self.send_sync('第一次同步配置')


if __name__ == '__main__':
    c = ClientLinux('4FF902ECDBFD17071147C85D14E48D5600000000')
    c.run()
    while 1:
        time.sleep(6)
        res = c.send_heart_beet_second('发送心跳')
        # c.send_sync('第二次同步配置')
        time.sleep(6)
        print(res)
