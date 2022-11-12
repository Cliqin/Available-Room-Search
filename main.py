import json
import jsonpath
import requests
import os
import sys
import traceback
from loguru import logger

import datetime
import time

import selenium.common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.relative_locator import locate_with

# 周次表示
weeks = {
    1: 1,
    2: 2,
    3: 4,
    4: 8,
    5: 16,
    6: 32,
    7: 64,
    8: 128,
    9: 256,
    10: 512,
    11: 1024,
    12: 2048,
    13: 4096,
    14: 8192,
    15: 16384,
    16: 32768,
    17: 65536,
    18: 131072,
    20: 262144,
    21: 524288,
}
# 星期几
week_list = [1, 2, 3, 4, 5, 6, 7]
# 节次字典
times_dic = {
    '上午12': 3,
    '上午34': 12,
    '下午56': 48,
    '下午78': 192,
    '晚上910': 1792
}
# 节次列表
times_list = ['上午12', '上午34', '下午56', '下午78', '晚上910']


def sorting(dic):
    # obj = json.load(open('result.json', 'r', encoding='utf-8'))
    # course_list = jsonpath.jsonpath(obj, '$..cdmc')
    course_list = []
    listing = json.loads(dic)['items']
    for i in listing:
        course_list.append(i['cdmc'])
    return course_list


class Normal:
    def __init__(self):
        self.last_list = {}
        self.final = ''

        self.pushplus = ['da9840d244194425bb1d1435fcd662da']

        timing = datetime.datetime.now()

        self.url = 'http://jwxt.gzhu.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?doType=query&gnmkdm=N2155'
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '249',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Cookie': '',
            'Host': 'jwxt.gzhu.edu.cn',
            'Origin': 'http://jwxt.gzhu.edu.cn',
            'Referer': 'http://jwxt.gzhu.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?gnmkdm=N2155&layout=default&su=32106100117',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.data = {
            'fwzt': 'cx',
            'xqh_id': '1',  # 校区
            'xnm': '2022',
            'xqm': '3',
            'cdlb_id': '11',
            # 'cdejlb_id': '',
            # 'qszws': '',
            # 'jszws': '',
            # 'cdmc': '',
            'lh': '6',  # 楼号
            'jyfs': '0',
            # 'cdjylx': '',
            'zcd': '',  # 周次 二进制
            'xqj': '',  # 星期几
            'jcd': '',  # 节次 二进制
            '_search': 'false',
            'nd': 1668063026809,
            'queryModel.showCount': '200',
            # 'queryModel.currentPage': '1',
            # 'queryModel.sortName': 'cdbh',
            # 'queryModel.sortOrder': 'asc',
            # 'time': '2'
        }

        self.page = 0
        self.flag = False

        # 星期几
        self.realweekday = (week_list[timing.weekday()])
        self.data['xqj'] = self.realweekday
        # 录入周次
        fp = open('weeklog.txt', 'r', encoding='utf-8')
        self.weeking = int(fp.read())
        fp.close()
        self.data['zcd'] = weeks[self.weeking]
        # 并判断是否调整周次
        if int(week_list[timing.weekday()]) == 7:
            fp = open('weeklog.txt', 'w', encoding='utf-8')
            fp.write(str(self.weeking + 1))
            fp.close()

    def steps(self, cookies):
        logger.info('输入cookies')
        self.headers['Cookie'] = cookies
        # 放入节次循环中
        logger.info('进入查询')
        for i in times_list:
            self.data['jcd'] = times_dic[i]
            print(self.data['zcd'], self.data['xqj'], self.data['jcd'])

            response = requests.post(self.url, headers=self.headers, data=self.data)

            # 摒弃依靠写入文件的存储模式
            # logger.info('打开文件写入')
            # with open('result.json', 'w', encoding='utf‐8') as fp:
            #     fp.write(response.text)
            # logger.info('正在解析中')

            self.last_list[i] = sorting(response.text)

        self.flag = True

    def output(self):
        print('星期', self.realweekday)
        print('************\n\n')

        logger.info('发送信息中')
        if self.flag:
            for i in times_list:
                self.final = self.final + str(i) + '\n' + str(self.last_list[i]) + '\n\n'
                print(i)
                print(self.last_list[i])
                print('************\n\n')

            if self.pushplus:
                for i in self.pushplus:
                    tim = datetime.datetime.now()
                    data = {"token": i, "title": f'{tim.month}月{tim.day}号空教室', "content": self.final + '龙哥,教我java'}
                    url = "http://www.pushplus.plus/send/"
                    logger.info(requests.post(url, data=data, timeout=10).text)
            else:
                logger.error('pushplus失效')
        else:
            if self.pushplus:
                for i in self.pushplus:
                    data = {"token": i, "title": '空教室查询失败',
                            "content": f'{logger.error(traceback.format_exc())}'}
                    url = "http://www.pushplus.plus/send/"
                    logger.info(requests.post(url, data=data, timeout=10).text)
            else:
                logger.error('pushplus失效')


if __name__ == '__main__':
    a = Normal()
    a.steps('JSESSIONID=9167C91EE5BA6D069FAA218B3A6C6170')
    a.output()
