# -*- coding:utf-8 -*-
"""
2018武侠特别活动
"""
from utils.mysql_util import mysql_util
import logging

try:
    from log.my_logger import modian_logger as my_logger
except:
    my_logger = logging.getLogger(__name__)
from utils import util
import os
import random
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Character:
    def __init__(self, modian_id, name, prop1=0, prop2=0, prop3=0, prop4=0, prop5=0):
        self.id = modian_id
        self.name = name
        self.prop1 = prop1  # 攻
        self.prop2 = prop2  # 防
        self.prop3 = prop3  # 气
        self.prop4 = prop4  # 运
        self.prop5 = prop5  # 魅力

    def __str__(self):
        return 'Character[modian_id=%s, name=%s, 攻=%s, 防=%s, 气=%s, 运=%s, 魅力=%s]' % (self.id, self.name, self.prop1,
                                                                                    self.prop2, self.prop3,
                                                                                    self.prop4, self.prop5)

    def use_good(self, good):
        """
        使用物品或学习技能
        :param good:
        :return:
        """
        my_logger.info('人物使用物品: %s' % good)
        self.prop1 += good.prop1
        self.prop2 += good.prop2
        self.prop3 += good.prop3
        self.prop4 += good.prop4
        self.prop5 += good.prop5


class Good:
    def __init__(self, name, prop1=0, prop2=0, prop3=0, prop4=0, prop5=0):
        self.name = name
        self.prop1 = prop1  # 攻
        self.prop2 = prop2  # 防
        self.prop3 = prop3  # 气
        self.prop4 = prop4  # 运
        self.prop5 = prop5  # 魅力

    def __str__(self):
        return 'Good[name=%s, 攻=%s, 防=%s, 气=%s, 运=%s, 魅力=%s]' % (self.name, self.prop1,
                                                                 self.prop2, self.prop3,
                                                                 self.prop4, self.prop5)

    def property_change(self):
        property_change_str = ''
        property_change_str += '攻+%s, ' % self.prop1 if self.prop1 > 0 else ''
        property_change_str += '防+%s, ' % self.prop2 if self.prop2 > 0 else ''
        property_change_str += '气+%s, ' % self.prop3 if self.prop3 > 0 else ''
        property_change_str += '运+%s, ' % self.prop4 if self.prop4 > 0 else ''
        property_change_str += '魅力+%s, ' % self.prop5 if self.prop5 > 0 else ''
        return property_change_str[:-1]


class Equipment(Good):
    """
    装备类物品
    """

    def __init__(self, name, prop1=0, prop2=0, prop3=0, prop4=0, prop5=0):
        super(Equipment, self).__init__(name, prop1, prop2, prop3, prop4, prop5)


class Item:
    """
    消耗类物品
    """

    def __init__(self, name, prop1=0, prop2=0, prop3=0, prop4=0, prop5=0):
        super(Item, self).__init__(name, prop1, prop2, prop3, prop4, prop5)


class Skill:
    """
    技能
    """

    def __init__(self, name, prop1=0, prop2=0, prop3=0, prop4=0, prop5=0):
        super(Skill, self).__init__(name, prop1, prop2, prop3, prop4, prop5)


class Event:
    def __init__(self, id, name, amount, weight):
        self.id = id
        self.name = name
        self.amount = amount
        self.weight = weight


def handle_event(pay_amount, character):
    result = ''
    event_list_j = event_json[str(pay_amount)]
    event_list = []
    weight_list = []
    for event_j in event_list_j:
        event = Event(event_j['id'], event_j['name'], pay_amount, event_j['weight'])
        event_list.append(event)
        weight_list.append(event_j['weight'])
    # 按概率选出是哪个大类的事件
    choice = util.weight_choice(event_list, weight_list)
    my_logger.debug('触发事件前属性: %s' % character)
    my_logger.info('触发事件: %s' % choice.name)

    if choice.id == 401:  # 个体-遇怪
        pass
    elif choice.id == 402:  # 个体-物品
        pass
    elif choice.id == 403:  # 互动-相识
        pass
    elif choice.id == 404:  # 互动-交恶
        pass
    elif choice.id == 405:  # 互动-PK
        pass
    elif choice.id == 301:  # 学艺-基础
        skill = util.choice(skill1_list)
        character.use_good(skill)
        result += '【{}】刻苦修炼，终于习得【{}】，{}\n'.format(character.name, skill.name,
                                                  skill.property_change())
        save_character(character)
    elif choice.id == 302:  # 学艺-进阶
        skill = util.choice(skill2_list)
        character.use_good(skill)
        result += '【{}】刻苦修炼，终于习得【{}】，{}\n'.format(character.name, skill.name,
                                                  skill.property_change())
        save_character(character)
    elif choice.id == 201:  # 门派
        mentor = util.choice(SCHOOLS)
        result += '【{}】骨骼精奇天资聪慧，{}对他青睐有加，亲自传授本门武功。\n【{}】获得真传，攻+35，防+30，气+30，运+20，魅力+40\n'.format(character.name,
                                                                                                 mentor, character.name)
        character.prop1 += 35
        character.prop2 += 30
        character.prop3 += 30
        character.prop4 += 20
        character.prop5 += 40
        save_character(character)
    elif choice.id == 101:  # 其他-得子
        name = ['子', '女', '哪吒']
        result += '行走江湖，总有意外，【{}】十月怀胎，诞下一{}。\n'.format(character.name, util.choice(name))
    elif choice.id == 102:  # 其他-称号升级
        result += '【{}】武功日益精进，救死扶伤匡扶正义，昔日的【无名小侠】如今已【名震江湖】，魅力+88\n'.format(character.name, )
        character.prop5 += 88
        save_character(character)
    my_logger.debug('触发事件后属性: %s' % character)
    return result


def created(modian_id):
    """
    是否创建人物，以摩点id判断
    :param modian_id: 摩点id
    :return:
    """
    my_logger.info('查询人物是否创建，modian_id: %s' % modian_id)
    rst = mysql_util.select_one("""
        SELECT * FROM `t_character` WHERE modian_id=%s
    """, (modian_id,))
    my_logger.debug(type(rst))
    my_logger.debug(rst)
    # my_logger.debug('rst: %s' % rst)
    if rst and len(rst) > 0:
        return True, Character(modian_id, str(rst[1], encoding='utf-8'), rst[2], rst[3], rst[4], rst[5], rst[6])
    else:
        return False, None


def create_character(modian_id):
    """
    创建人物
    :return:
    """
    my_logger.info('创建人物, modian_id: %s' % modian_id)
    # 随机姓名
    random_name = TOTAL_NAMES.pop()
    my_logger.debug('随机姓名: %s' % random_name)
    # 随机生成属性
    prop1 = random.randint(40, 70)
    prop2 = random.randint(30, 60)
    prop3 = random.randint(5, 20)
    prop4 = random.randint(0, 50)
    prop5 = random.randint(30, 50)
    mysql_util.query("""
        INSERT INTO `t_character` (`modian_id`, `name`, `prop1`, `prop2`, `prop3`, `prop4`, `prop5`)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (modian_id, random_name, prop1, prop2, prop3, prop4, prop5))

    intro_words = [
        "郁雷之声渐响，轰轰不绝。河海尚远，而耳中尽是浪涛之声。 似有一名字伴雷声入耳，仔细辨来，名为：【{}】。".format(random_name),
        "湖山深处,但见竹木阴森,苍翠重叠,不雨而润,不烟而晕, 晨雾朦胧处现一少年，“在下【{}】，请问此处可是星梦谷？”".format(random_name),
        "月照竹林风飞叶，竹影之下见刀光。小侠籍籍无名，仅有此片竹林识得其名为【{}】".format(random_name),
        "嗖的一声，一支羽箭从山坳后射了出来，呜呜声响，划过长空，【{}】松开弓弦，雁落平沙。".format(random_name),
        "灯宵月夕，雪际花时，市集喧闹却也听得句柔声细语：“这文书写有【{}】之名，可是你掉的？”".format(random_name)
    ]
    # 随机挑选一个出场方式
    intro = util.choice(intro_words)
    report_str = '%s\n' % intro[0]
    report_str += '%s的武侠世界开启, 属性：\n攻: %s, 防: %s, 气: %s, 运: %s, 魅力: %s\n' % (
        random_name, prop1, prop2, prop3, prop4, prop5)
    return report_str


def donate(modian_id, pay_amount):
    MIN_AMOUNT = 1
    rst = ''
    has_created, character = created(modian_id)
    if has_created:
        my_logger.info('已经创建了人物: %s' % modian_id)
        # 如果已经创建
        my_logger.debug('%s触发了随机事件（施工中）' % character.name)
        if pay_amount < MIN_AMOUNT:
            return ''
        tmp = pay_amount
        amounts = [200, 100, 50, 10]
        max_event = 3  # 最多触发3次事件
        idx = 0
        while max_event > 0:
            event_time = int(tmp / amounts[idx])
            event_time = max_event if event_time > max_event else event_time
            for i in range(event_time):
                handle_event(amounts[idx], character)
            max_event -= event_time
            tmp = tmp % amounts[idx]
            idx += 1
    else:
        my_logger.info('未创建人物, modian_id: %s' % modian_id)
        if pay_amount >= MIN_AMOUNT:
            rst = create_character(modian_id)
    return rst


def sync_names():
    """
    程序启动时，本地和db同步下已使用的姓名
    :return:
    """
    global TOTAL_NAMES
    # 从DB获取已使用的姓名
    rst = mysql_util.select_all("""
        SELECT `name` from `t_character`;
    """)
    my_logger.debug(type(rst))
    my_logger.debug(rst)
    # my_logger.debug('names in db: %s' % rst)
    name_used = []
    if rst:
        for a in rst:
            name_used.append(str(a[0], encoding='utf-8'))
    my_logger.debug('name_used: %s' % name_used)
    # name_used = ['刘超', '李凡']
    # return list1 - list2
    total_copy = TOTAL_NAMES.copy()
    TOTAL_NAMES = total_copy.difference(set(name_used))


def save_character(character):
    """
    将更新后的任务保存到数据库
    :param character:
    :return:
    """
    my_logger.debug('将更新后的任务保存到数据库')
    mysql_util.query("""
        UPDATE `t_character` SET `name`=%s, `prop1`=%s, `prop2`=%s, `prop3`=%s, `prop4`=%s, `prop5`=%s
            WHERE `modian_id`=%s
    """, (character.name, character.prop1, character.prop2, character.prop3, character.prop4, character.prop5,
          character.id))


def read_skill_list():
    # 读取招式列表
    skill1_raw = util.read_txt(os.path.join(BASE_DIR, 'data', 'wuxia', 'skill1.txt'))
    skill2_raw = util.read_txt(os.path.join(BASE_DIR, 'data', 'wuxia', 'skill2.txt'))
    skill1_list = []
    skill2_list = []
    for line in skill1_raw:
        strs = line.split(',')
        skill = Skill(strs[0], int(strs[1]), int(strs[2]), int(strs[3]), int(strs[4]), int(strs[5]))
        skill1_list.append(skill)
    for line in skill2_raw:
        strs = line.split(',')
        skill = Skill(strs[0], int(strs[1]), int(strs[2]), int(strs[3]), int(strs[4]), int(strs[5]))
        skill2_list.append(skill)
    return skill1_list, skill2_list


TOTAL_NAMES = set(util.read_txt(os.path.join(BASE_DIR, 'data', 'wuxia', 'names.txt')))
event_json = json.load(open(os.path.join(BASE_DIR, 'data', 'wuxia', 'event.json'), encoding='utf-8'))
SCHOOLS = util.read_txt(os.path.join(BASE_DIR, 'data', 'wuxia', 'school.txt'))
skill1_list, skill2_list = read_skill_list()
sync_names()

if __name__ == '__main__':
    # sync_names()
    print(create_character('123456'))
