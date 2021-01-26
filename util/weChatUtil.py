#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
from util.logUtil import logger
import requests

token_file_path = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/common/access_token.conf')


class WeChat:
    def __init__(self):
        self.CORPID = 'wwb648db66ac208536'  # 企业ID，在管理后台获取
        self.CORPSECRET = 'pqSaZyq3XOTUhLuFRwLpmc6z0QjmxnqhikmO-jnidTs'  # 自建应用的Secret，每个自建应用里都有单独的secret
        self.AGENTID = '1000002'  # 应用ID，在后台应用中获取
        self.TOUSER = "@all"  # 接收者用户名,多个用户用|分割

    def _get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def get_access_token(self):
        """
        获取token，有效期为2小时，超过两小时则重新获取
        :return:
        """
        try:
            with open(token_file_path, 'r') as f:
                t, access_token = f.read().split()
        except:
            with open(token_file_path, 'w') as f:
                access_token = self._get_access_token()
                cur_time = time.time()
                f.write('\t'.join([str(cur_time), access_token]))
                return access_token
        else:  # 无异常时执行的代码
            cur_time = time.time()
            if 0 < cur_time - float(t) < 7200:
                return access_token
            else:
                with open(token_file_path, 'w') as f:
                    access_token = self._get_access_token()
                    f.write('\t'.join([str(cur_time), access_token]))
                    return access_token

    def send_data(self, message):
        if len(message.strip()) == 0:
            return
        logger.info("发送微信消息: " + message)
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": self.TOUSER,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msg = (bytes(json.dumps(send_values), 'utf-8'))
        response = requests.post(send_url, send_msg)
        response = response.json()  # 当返回的数据是json串的时候直接用.json即可将respone转换成字典
        if 'ok' != response["errmsg"]:
            raise Exception('发送微信消息失败：' + response["errmsg"])


weChatClient = WeChat()
