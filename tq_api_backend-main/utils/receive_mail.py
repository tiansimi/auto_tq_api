# -*- coding:utf-8 -*-
import email
import imaplib
import time

import allure

from utils.log import log


class ReceiveMail:
    """ 接收邮件 """

    # 解析邮件内容
    def get_body(self, imap_conn):
        imap_conn.list()  # 列出邮箱中所有的列表，如：收件箱、垃圾箱、草稿箱。。。
        imap_conn.select('INBOX')  # 选择收件箱（默认）
        result, dataid = imap_conn.search('search', None, "ALL")
        mailidlist = dataid[0].split()  # 转成标准列表,获得所有邮件的ID
        log.info('{},----------{}-----------------{}'.format(result, dataid, mailidlist))

        last = mailidlist[-1]
        result, data = imap_conn.fetch(last, '(RFC822)')  # 通过邮件id获取邮件
        log.info(f'{result},-----------------{data}')
        e = email.message_from_bytes(data[0][1])
        subject = email.header.make_header(email.header.decode_header(e['SUBJECT']))
        mail_from = email.header.make_header(email.header.decode_header(e['From']))
        body = str(self.get_bodys(e), encoding='utf-8')  # utf-8 gb2312 GB18030解析中文日文英文
        log.info(f'邮件主题：{subject}')
        log.info(f'邮件内容：{body}')
        log.info(f'邮件发件人：{mail_from}')

        imap_conn.store(last, '+FLAGS', '\\Deleted')

        imap_conn.close()
        imap_conn.logout()

        return subject, body

    def get_bodys(self, msg):
        if msg.is_multipart():
            return self.get_bodys(msg.get_payload(0))
        else:
            return msg.get_payload(None, decode=True)

    def connect_mail(self):
        host = 'smtp.exmail.qq.com'
        port = 465
        user = 'zhouyueru@huorong.cn'
        pwd = 'Zhouyr.123'
        try:
            mail_imap = imaplib.IMAP4_SSL(host=host)
            log.info('邮箱连接成功{}'.format(mail_imap.welcome))
        except Exception as e:
            log.info('邮箱连接失败{}'.format(e))
        else:
            mail_imap.login(user=user, password=pwd)
            time.sleep(8)
            subject, body = self.get_body(mail_imap)
            return subject, body

    def receive_mail(self, img_info, email_header):
        with allure.step(img_info):
            allure.attach('接收邮件', '{}'.format(img_info))
            subject, body = self.connect_mail()
            if email_header == subject:
                log.info(f'断言成功 -期望：{email_header} - 实际：{subject}')
            else:
                log.error(f'断言失败 -期望:{email_header} -实 际:{subject}')
            assert email_header == subject


if __name__ == '__main__':
    mail_imap = ReceiveMail()
    mail_imap.connect_mail()
