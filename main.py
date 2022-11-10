import os
import sys
import time
import traceback
from selenium import webdriver
import requests
import selenium.webdriver
from loguru import logger
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.wait import WebDriverWait


class Free:

    def __init__(self):
        self.xuhao = str("32106100117")
        self.mima = str('Aa18319093951!')
        # self.pushplus = str('da9840d244194425bb1d1435fcd662da')

        path = 'chromedriver.exe'
        self.driver = webdriver.Chrome(path)
        self.wdwait = WebDriverWait(self.driver, 30)
        # self.driver.get('https://baidu.com')

        self.page = 0
        self.fail = False

    def __call__(self):
        # 总共执行5次
        for retries in range(5):
            try:
                logger.info(f"第{retries + 1}次运行")
                if retries:
                    self.refresh()

                if self.page == 0:
                    # 登陆操作
                    self.step1()

                if self.page in [0, 1]:
                    self.step2()

                    break
            except Exception:
                logger.error(traceback.format_exc())
                logger.error(f'第{retries + 1}次运行失败，当前页面标题为：{self.driver.title}')
                if retries == 4:
                    self.fail = True

    def refresh(self):
        refresh_times = 0
        while True:
            logger.info('刷新页面')
            self.driver.refresh()

            title = self.driver.title
            if title == '融合门户':
                self.page = 1
            elif title == '学生健康状况申报':
                self.page = 2
            elif title in ['填报健康信息 - 学生健康状况申报', '表单填写与审批::加载中']:
                self.page = 3
            elif title == "":
                logger.info('当前页面标题为：')

                refresh_times += 1
                if refresh_times < 4:
                    continue
            else:
                self.page = 0

            break

        logger.info(f'当前页面标题为：{title}')

    # 登陆操作
    def step1(self):
        logger.info('正在转到统一身份认证页面')
        self.driver.get(
            'https://newcas.gzhu.edu.cn/cas/login?service=https%3A%2F%2Fnewmy.gzhu.edu.cn%2Fup%2Fview%3Fm%3Dup'
        )

        self.wdwait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='robot-mag-win small-big-small']")))

        logger.info('正在尝试登陆融合门户')
        for script in [
            f"document.getElementById('un').value='{self.xuhao}'",
            f"document.getElementById('pd').value='{self.mima}'",
            "document.getElementById('index_login_btn').click()"
        ]:
            self.driver.execute_script(script)
        print('**************', self.driver.title)

    def step2(self):
        self.wdwait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//a[@title="教务系统"]/img')))

        logger.info('正在转到教务系统')
        self.driver.find_elements(by=By.XPATH, value='//a[@title="教务系统"]')[0].click()
        # print(self.driver.get_cookies())
        # time.sleep(80)
        # # self.wdwait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_yd"]')))
        # # self.driver.find_elements(by=By.XPATH, value='//*[@id="btn_yd"]')[0].click()
        # self.driver.get('http://jwxt.gzhu.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=&_t=1668059002212')
        # time.sleep(5)
        # print('**************', self.driver.title)
        print(self.driver.get_cookie())

if __name__ == '__main__':
    f = Free()
    f()
