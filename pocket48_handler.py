# -*- coding:utf-8 -*-

import requests
import json

from config_reader import ConfigReader
import time
from qqhandler import QQHandler
from qqbot.utf8logger import INFO,ERROR,DEBUG

import sys

reload(sys)
sys.setdefaultencoding('utf8')


class Pocket48Handler:
    def __init__(self, auto_reply_groups, member_room_msg_groups, member_room_comment_msg_groups):
        self.last_monitor_time = -1
        self.auto_reply_groups = auto_reply_groups
        self.member_room_msg_groups = member_room_msg_groups
        self.member_room_comment_msg_groups = member_room_comment_msg_groups
        self.member_room_msg_ids = []
        self.member_room_comment_ids = []
        self.member_live_ids = set()

    def get_member_live_msg(self):
        """
        获取所有直播间信息
        :return:
        """
        url = 'https://plive.48.cn/livesystem/api/live/v1/memberLivePage'
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': '863526430773465',
            'token': '1HMD6/i9yO4b2myk2c7K9seuVtXP+QCpqxRpB8ja8dQDLWR0RXXobiz87FeoVYYYOY4eAF9ifbM=',
            'version': '4.1.2',
            'Content-Type': 'application/json;charset=utf-8',
            'Content-Length': '89',
            'Host': 'plive.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cache-Control': 'no-cache'
        }
        params = {
            "giftUpdTime": 1503766100000,
            "groupId": 0,  # SNH48 Group所有人
            "lastTime": 0,
            "limit": 50,
            "memberId": 0,
            "type": 0
        }
        try:
            response = requests.post(url, data=json.dumps(params), headers=header, verify=False)
        except Exception as e:
            ERROR('获取成员直播失败')
            ERROR(e)
        return response.text

    def get_member_room_msg(self, room_id):
        """
        获取成员房间消息
        :param room_id: 房间id
        :return:
        """
        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/chat'
        params = {
            "roomId": room_id, "lastTime": 0, "limit": 10
        }
        try:
            response = requests.post(url, data=json.dumps(params), headers=self.header_args(), verify=False)
        except Exception as e:
            ERROR('获取成员消息失败')
            ERROR(e)
        return response.text

    def init_msg_queues(self, room_id):
        """
        初始化房间消息队列
        :param room_id:
        :return:
        """
        try:
            r1 = self.get_member_room_msg(room_id)
            r2 = self.get_member_room_comment(room_id)

            r1_json = json.loads(r1)
            r2_json = json.loads(r2)
            for r in r1_json['content']['data']:
                msg_id = r['msgidClient']
                self.member_room_msg_ids.append(msg_id)

            for r in r2_json['content']['data']:
                msg_id = r['msgidClient']
                self.member_room_comment_ids.append(msg_id)

            DEBUG('成员消息队列: %s', len(self.member_room_msg_ids))
            DEBUG('房间评论队列: %s', len(self.member_room_comment_ids))
        except Exception as e:
            ERROR('初始化消息队列失败')
            ERROR(e)

    def parse_room_msg(self, response):
        """
        对成员消息进行处理
        :param response:
        :return:
        """
        # DEBUG(response)
        rsp_json = json.loads(response)
        msgs = rsp_json['content']['data']

        message = ''
        for msg in msgs:
            extInfo = json.loads(msg['extInfo'])
            # platform = extInfo['platform']
            msg_id = msg['msgidClient']

            # bodys = json.loads(msg['bodys'])
            # temp_timestamp = self.convert_timestamp(self.last_monitor_time)
            # if self.last_monitor_time < 0 or msg['msgTime'] < temp_timestamp:
            #     break
            # 判断是否为成员
            if msg_id in self.member_room_msg_ids:
                continue
            DEBUG('成员消息')
            self.member_room_msg_ids.append(msg_id)
            DEBUG('extInfo.keys():' + ','.join(extInfo.keys()))
            if 'text' in extInfo.keys():  # 普通消息
                DEBUG('普通消息')
                message += '【成员消息】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], extInfo['text'])
            elif 'messageText' in extInfo.keys():  # 翻牌消息
                DEBUG('翻牌')
                member_msg = extInfo['messageText']
                fanpai_msg = extInfo['faipaiContent']
                fanpai_id = extInfo['faipaiName']
                message += '【翻牌】[%s]-%s\n【被翻牌】冯晓菲的%s:%s\n' % (msg['msgTimeStr'], member_msg, fanpai_id, fanpai_msg)
            else:
                is_json = self.check_json_format(msg['bodys'])
                bodys = json.loads(msg['bodys'])
                if 'url' in bodys.keys():
                    url = bodys['url']
                    DEBUG('图片')
                    message += '【图片】[%s]-%s\n' % (msg['msgTimeStr'], url)
                else:
                    DEBUG('房间语音')

        if message and len(self.member_room_msg_groups) > 0:
            QQHandler.send_to_groups(self.member_room_msg_groups, message)
        INFO('message: %s', message)
        DEBUG('成员消息队列: %s', len(self.member_room_msg_ids))

    def parse_room_comment(self, response):
        """
        对房间评论进行处理
        :param response:
        :return:
        """
        rsp_json = json.loads(response)
        msgs = rsp_json['content']['data']

        message = ''
        for msg in msgs:
            extInfo = json.loads(msg['extInfo'])
            platform = extInfo['platform']
            msg_id = msg['msgidClient']

            if msg_id in self.member_room_comment_ids:
                continue
            DEBUG('房间评论')
            self.member_room_comment_ids.append(msg_id)
            message += '【房间评论】[%s]-%s: %s\n' % (msg['msgTimeStr'], extInfo['senderName'], extInfo['text'])

        INFO('message: %s', message)
        if message and len(self.member_room_comment_msg_groups) > 0:
            QQHandler.send_to_groups(self.member_room_comment_msg_groups, message)
        DEBUG('房间评论队列: %s', len(self.member_room_comment_ids))

    def get_member_room_comment(self, room_id):
        """
        获取成员房间的粉丝评论
        :param room_id: 房间id
        :return:
        """
        url = 'https://pjuju.48.cn/imsystem/api/im/v1/member/room/message/comment'
        params = {
            "roomId": room_id, "lastTime": 0, "limit": 10
        }
        # 收到响应
        try:
            response = requests.post(url, data=json.dumps(params), headers=self.header_args(), verify=False)
        except Exception as e:
            ERROR('获取房间评论失败')
            ERROR(e)
        return response.text

    def parse_member_live(self, response, member_id):
        """
        对直播列表进行处理，找到正在直播的指定成员
        :param member_id:
        :param response:
        :return:
        """
        rsp_json = json.loads(response)
        # 当前没有人在直播
        if 'liveList' not in rsp_json.keys():
            DEBUG('当前没有人在直播')
            return
        live_list = rsp_json['content']["liveList"]
        msg = ''
        for live in live_list:
            live_id = live['liveId']
            if live['memberId'] == member_id and live_id not in self.member_live_ids:
                DEBUG('[直播]member_id: %s, live_id: %', member_id, live_id)
                start_time = self.convert_timestamp_to_timestr(live['startTime'])
                stream_path = live['streamPath']  # 流地址
                sub_title = live['subTitle']  # 直播名称
                type = live['liveType']
                if type == 1:  # 露脸直播
                    msg += '你的小宝贝儿开露脸直播了: %s\n开始时间: %s' % (sub_title, start_time)
                elif type == 2:  # 电台直播
                    msg += '你的小宝贝儿开电台直播了: %s\n开始时间: %s' % (sub_title, start_time)
                self.member_live_ids.add(live_id)
        if msg and len(self.member_room_msg_groups) > 0:
            QQHandler.send_to_groups(self.member_room_msg_groups, msg)

    def convert_timestamp_to_timestr(self, timestamp):
        """
        将13位时间戳转换为字符串
        :param timestamp:
        :return:
        """
        timeArray = time.localtime(timestamp / 1000)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return time_str

    def is_member(self, role):
        """
        判断是否为成员
        :param role: 成员为1
        :return:
        """
        return role == 1

    def convert_timestamp(self, timestamp):
        """
        将10位时间戳转化为13位
        :param timestamp:
        :return:
        """
        return timestamp * 1000

    def check_json_format(self, raw_msg):
        """
        判断给定字符串是不是符合json格式
        :param raw_msg:
        :return:
        """
        DEBUG('function: %s', __name__)
        if isinstance(raw_msg, str):  # 首先判断变量是否为字符串
            try:
                json.loads(raw_msg, encoding='utf-8')
            except ValueError, e:
                ERROR(e)
                return False
            DEBUG('is json')
            return True
        else:
            DEBUG('is not string')
            return False

    def header_args(self):
        """
        构造请求头信息
        :return:
        """
        header = {
            'os': 'android',
            'User-Agent': 'Mobile_Pocket',
            'IMEI': '863526430773465',
            'token': '1HMD6/i9yO4b2myk2c7K9seuVtXP+QCpqxRpB8ja8dQDLWR0RXXobiz87FeoVYYYOY4eAF9ifbM=',
            'version': '4.1.2',
            'Content-Type': 'application/json;charset=utf-8',
            'Content-Length': '42',
            'Host': 'pjuju.48.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cache-Control': 'no-cache'
        }
        return header


if __name__ == '__main__':
    handler = Pocket48Handler([], [], [])
    response = handler.get_member_live_msg()
    handler.parse_member_live(response, 417317)
    # print handler.convert_timestamp_to_timestr(1504970619679)
