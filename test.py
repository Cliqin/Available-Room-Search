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


class Search:

    def __init__(self):
        '''设置无头浏览'''
        options = Options()
        optionsList = [
            "--headless",
            "--enable-javascript",
            "start-maximized",
            "--disable-gpu",
            "--blink-settings=imagesEnabled=false",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-browser-side-navigation",
            "--disable-dev-shm-usage",
        ]
        for option in optionsList:
            options.add_argument(option)

        options.page_load_strategy = 'none'
        options.add_experimental_option(
            "excludeSwitches", ["ignore-certificate-errors", "enable-automation"]
        )

        path = 'chromedriver.exe'
        self.driver = webdriver.Chrome(options=options)
        # self.driver = webdriver.Chrome(path)

        '''用户信息'''

        self.xuhao = str("32106100117")
        self.mima = str('Aa18319093951!')
        # self.pushplus = ['da9840d244194425bb1d1435fcd662da', '50ed8dfec78243959c88914a9d61ac13']
        self.pushplus = ['da9840d244194425bb1d1435fcd662da']
        self.wdwait = WebDriverWait(self.driver, 90)
        self.titlewait = WebDriverWait(self.driver, 30)

        """浏览器信息"""
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
        '''请求参数'''
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

        '''其他数据'''
        # 存储最后的数据
        self.last_list = {}
        self.final = ''

        '''页面数据'''
        self.page = 0
        self.flag = False

        timing = datetime.datetime.now()

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

    def login(self):
        for retries in range(5):
            try:
                logger.info(f"第{retries + 1}次运行")
                if retries:
                    self.refresh()
                if self.flag:
                    return

                # 是否在初始页面
                if self.page == 0:
                    # 访问统一身份验证
                    self.step0()
                # 是否继续或者在融合门户
                if self.page in [0, 1]:
                    # 当前在统一身份验证,现在执行登陆
                    self.step1()
                if self.page in [0, 1, 2]:
                    self.step2()
                if self.page in [0, 1, 2, 3]:
                    self.step3()
                if self.page in [0, 1, 2, 3, 4]:
                    self.step4()

            except selenium.common.exceptions.TimeoutException:
                logger.error(traceback.format_exc())

                if not self.driver.title:
                    logger.error(f"第{retries + 1}次运行失败，当前页面标题为空")
                else:
                    logger.error(f"第{retries + 1}次运行失败，当前页面标题为：{self.driver.title}")

                if retries == 4:
                    self.flag = False
                    logger.info('发送失败消息')
                    self.output()

        self.driver.quit()

    def refresh(self):
        """刷新页面，直到页面标题不为空

        Raises:
            selenium.common.exceptions.TimeoutException: 页面刷新次数达到上限
        """
        refresh_times = 0

        while True:
            logger.info('刷新页面')
            self.driver.refresh()

            try:
                self.titlewait.until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "title"))
                )
            except selenium.common.exceptions.TimeoutException:
                pass

            title = self.driver.title

            # 判断是否查询成功
            if self.flag:
                logger.info('发送成功消息')
                self.output()
                return

            match title:
                case 'Unified Identity Authentication':
                    self.page = 1
                    logger.info(f'1已重置page为:{self.page}')
                case '统一身份认证':
                    self.page = 1
                    logger.info(f'2已重置page为:{self.page}')
                case '融合门户':
                    self.page = 2
                    logger.info(f'已重置page为:{self.page}')
                case '广州大学教学综合信息服务平台':
                    self.page = 3
                    logger.info(f'已重置page为:{self.page}')
                case '查询空闲教室':
                    self.page = 4
                    logger.info(f'已重置page为:{self.page}')
                case "":
                    logger.info('match函数匹配失败')
                    logger.info(f'当前页面标题为：{title}')
                    refresh_times += 1
                    if refresh_times < 5:
                        continue
                    raise selenium.common.exceptions.TimeoutException("页面刷新次数达到上限")
                case _:
                    self.page = 0
                    logger.info(f'已重置page为:{self.page}')
            break
        logger.info(f'*最后*当前页面标题为：{title},当前的页面编号为:{self.page}')

    def step0(self):
        """转到统一身份认证界面"""
        logger.info('第零步:直接跳转登录页面')
        logger.info('正在转到统一身份认证页面')
        self.driver.get(
            'https://newcas.gzhu.edu.cn/cas/login?service=https%3A%2F%2Fnewmy.gzhu.edu.cn%2Fup%2Fview%3Fm%3Dup'
        )
        '''统一身份认证'''

    def step1(self):
        logger.info(f'当前的标题为:{self.driver.title}')
        logger.info('正在搜索Unified Identity Authentication标题')
        self.titlewait.until(EC.title_contains("Unified Identity Authentication"))
        logger.info('正在搜索是否有机器人图标')
        self.wdwait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='robot-mag-win small-big-small']")
            )
        )

        '''统一身份认证'''
        logger.info('正在尝试登陆融合门户')
        for script in [
            f"document.getElementById('un').value='{self.xuhao}'",
            f"document.getElementById('pd').value='{self.mima}'",
            "document.getElementById('index_login_btn').click()"
        ]:
            self.driver.execute_script(script)
        logger.info('点了登陆之后再等10秒')
        time.sleep(10)
        '''统一身份认证'''

    def step2(self):
        '''融合门户'''
        logger.info(f'当前的标题为:{self.driver.title}')
        logger.info('正在搜索融合门户标题')
        self.titlewait.until(EC.title_contains("融合门户"))
        # logger.info('正在搜索教务系统图标')
        # self.wdwait.until(EC.visibility_of_element_located((By.XPATH, '//a[@title="教务系统"]/img')))
        logger.info('正在转到教务系统')
        time.sleep(5)
        # 直接跳转到教务系统
        # self.driver.find_elements(by=By.XPATH, value='//a[@title="教务系统"]')[0].click()
        self.driver.get('http://jwxt.gzhu.edu.cn/sso/driot4login')

    def step3(self):
        ''''cookies'''
        logger.info(f'当前的标题为:{self.driver.title}')
        logger.info('正在搜索广州大学教学综合信息服务平台标题')      
        self.titlewait.until(EC.title_contains("广州大学教学综合信息"))
        '''广州大学教学综合信息服务平台'''
        logger.info('提取cookies')
        temp_url = 'http://jwxt.gzhu.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?gnmkdm=N2155&layout=default&su=32106100117'
        self.driver.get(temp_url)

    def step4(self):
        self.titlewait.until(EC.title_contains("空闲教室"))
        logger.info('获取cookies')
        test = self.driver.get_cookies()
        print('cookies为:', test)
        cookies = test[0]['name'] + '=' + test[0]['value']
        self.steps(cookies=cookies)

    '''关键步骤'''

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

    '''输出与调整'''

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
    r = Search()
    r.login()
