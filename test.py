import json
import traceback

import jsonpath
import datetime
import time
from selenium import webdriver
import requests
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

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


def sorting():
    obj = json.load(open('result.json', 'r', encoding='utf-8'))
    course_list = jsonpath.jsonpath(obj, '$..cdmc')
    return course_list


class Search():
    def __init__(self):
        '''设置无头浏览'''
        options = Options()
        optionsList = [
            "--headless",
            "--enable-javascript",
            "start-maximized",
            "--disable-gpu",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-browser-side-navigation",
            "--disable-dev-shm-usage"
        ]
        for option in optionsList:
            options.add_argument(option)
        options.page_load_strategy = 'none'
        options.add_experimental_option(
            "excludeSwitches",
            ["ignore-certificate-errors", "enable-automation"])
        self.driver = webdriver.Chrome(options=options)

        '''用户信息'''
        path = 'chromedriver.exe'
        self.xuhao = str("32106100117")
        self.mima = str('Aa18319093951!')
        self.pushplus = str('da9840d244194425bb1d1435fcd662da')
        self.wdwait = WebDriverWait(self.driver, 60)

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
        self.fail = False

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
        for retries in range(10):
            try:
                logger.info(f"第{retries + 1}次运行")
                if retries:
                    '''刷新'''

                if self.page == 0:
                    self.step1()
                if self.page in [0, 1]:
                    self.step2()
            except Exception:
                logger.error(traceback.format_exc())
                logger.error(f'第{retries + 1}次运行失败，当前页面标题为：{self.driver.title}')

                if retries == 9:
                    self.fail = True

    def refresh(self):
        refresh_time = 0

        while True:
            logger.info('刷新页面')
            self.driver.refresh()

            title = self.driver.title
            if title == '统一身份认证':
                self.page = 1
            elif title == '融合门户':
                self.page = 2
            else:
                self.page = 0

    def step1(self):
        logger.info('正在转到统一身份认证页面')
        self.driver.get(
            'https://newcas.gzhu.edu.cn/cas/login?service=https%3A%2F%2Fnewmy.gzhu.edu.cn%2Fup%2Fview%3Fm%3Dup'
        )
        '''统一身份认证'''
        self.wdwait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='robot-mag-win small-big-small']")))

        '''统一身份认证'''
        logger.info('正在尝试登陆融合门户')
        for script in [
            f"document.getElementById('un').value='{self.xuhao}'",
            f"document.getElementById('pd').value='{self.mima}'",
            "document.getElementById('index_login_btn').click()"
        ]:
            self.driver.execute_script(script)
        '''统一身份认证'''

    def step2(self):
        '''融合门户'''
        self.wdwait.until(EC.visibility_of_element_located((By.XPATH, '//a[@title="教务系统"]/img')))
        logger.info('正在转到教务系统')
        self.driver.find_elements(by=By.XPATH, value='//a[@title="教务系统"]')[0].click()
        '''融合门户'''

        '''cookies'''
        logger.info('提取cookies')
        temp = self.driver.get_cookies()
        time.sleep(2)
        temp_url = 'http://jwxt.gzhu.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?gnmkdm=N2155&layout=default&su=32106100117'
        self.driver.get(temp_url)
        test = self.driver.get_cookies()
        cookies = test[0]['name'] + '=' + test[0]['value']

        self.steps(cookies=cookies)

    '''关键步骤'''

    def steps(self, cookies):
        logger.info('变换cookies')
        self.headers['Cookie'] = cookies
        # 放入节次循环中
        logger.info('进入查询')
        for i in times_list:
            self.data['jcd'] = times_dic[i]
            print(self.data['zcd'], self.data['xqj'], self.data['jcd'])

            response = requests.post(self.url, headers=self.headers, data=self.data)
            # print(response.status_code)
            # print(response.text)
            logger.info('打开文件写入')
            with open('result.json', 'w', encoding='utf‐8') as fp:
                fp.write(response.text)
            logger.info('正在解析中')
            self.last_list[i] = sorting()

    '''输出与调整'''

    def output(self):
        print('星期', self.realweekday)
        print('************\n\n')

        for i in times_list:
            self.final = self.final + str(i) + '\n' + str(self.last_list[i]) + '\n\n'
            print(i)
            print(self.last_list[i])

            print('************\n\n')

        logger.info('发送信息中')
        if self.pushplus:
            tim = datetime.datetime.now()
            data = {"token": self.pushplus, "title": f'{tim.month}月{tim.day}号空教室', "content": self.final}
            url = "http://www.pushplus.plus/send/"
            logger.info(requests.post(url, data=data, timeout=10).text)


if __name__ == '__main__':
    r = Search()
    r.step1()
    r.step2()
    r.output()
