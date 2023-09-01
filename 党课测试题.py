# coding=gbk
# @Time : 2021-04-22 17:09
# @Author : ZAH
# @File : 党课测试题.py
# @Software : PyCharm
import hashlib

import requests
import re
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from retry import retry

url = 'http://wldx.beihua.edu.cn/m/Exam/Student/Login'
my_study_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/MyStudy'
ti_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/AnswerCard'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/69.0.3493.3 Safari/537.36 '
}

def md5(plaintext):
    hl = hashlib.md5()
    hl.update(plaintext.encode(encoding='utf-8'))
    return hl.hexdigest()


def study_time():
    my_study_page = session.get(url=my_study_url, headers=headers).text
    tree = etree.HTML(my_study_page)
    study = tree.xpath('//div[@class="item-title label text-align-r"]/text()')
    print('姓名:' + study[0] + '\n')
    print('性别:' + study[1] + '\n')
    print('学号:' + study[2] + '\n')
    print('学习时间:' + study[3] + '\n')
    return study[3]


@retry(delay=2)
def dangke_question():
    login_data = {
        'LoginName': LoginName,
        'password': md5(password)
    }
    login = session.post(url=url, headers=headers, data=login_data)
    study_time()
    bro.get('http://wldx.beihua.edu.cn/m/Exam/Student/Login#')
    WebDriverWait(bro, 5).until(EC.presence_of_element_located((By.ID, 'LoginName')))
    search_input = bro.find_element_by_id('LoginName')
    search_input.send_keys(LoginName)
    search_input = bro.find_element_by_id('Password')
    search_input.send_keys(password)
    login = bro.find_element_by_css_selector('.button')
    login.click()


@retry(delay=2)
def panduan():
    if admin == '1':
        # 入党积极分子培训
        bro.get('http://wldx.beihua.edu.cn/m/Exam/Student/PracticeList?courseID=19647dda-e696-4e4c-96e5-213dea415fe5')
    if admin == '2':
        # 发展对象培训
        bro.get('http://wldx.beihua.edu.cn/m/Exam/Student/PracticeList?courseID=25961f95-9cdc-4e63-9443-91a63406bf5e')
    WebDriverWait(bro, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.zt')))
    dt = bro.find_element_by_css_selector('.zt')
    dt.click()
    sleep(5)
    # 题数 80 或 800
    if admin == '1':
        num = 800
    if admin == '2':
        num = 80
    for i in range(0, num):
        q_type_list = bro.find_elements_by_class_name('list-block')
        for q_type in q_type_list:
            if q_type.get_attribute('style') == 'display: block;':
                q_type = q_type.get_attribute('id')
                break
        answer(q_type)
        # 最后一题
        if i == (num-1):
            # 刷新界面
            bro.refresh()
            continue
        bro.find_element_by_xpath("//*[contains(text(),'下一题')]").click()


def answer(a):
    data = {
        'ID': '',
        'answer': ''
    }

    if a == 'oneCheck':
        s = list(bro.find_element_by_xpath('//*[@id="oneCheckul"]/li[1]/div[2]/div[1]').find_element_by_tag_name(
            'input').get_attribute('id'))
        del (s[-1])
        data.update(ID=''.join(md5(s)))
        value = bro.find_element_by_id('answerText').get_attribute('textContent')
        value_li = bro.find_element_by_id('oneCheckul').find_elements_by_tag_name('li')
        value_list = []
        for value_ in value_li:
            value_list.append(value_.get_attribute('textContent'))
        data.update(answer=str(value_list.index(value)))
        print(data)
        session.post(url=ti_url, headers=headers, data=data)

    if a == 'mulitCheck':
        s = list(bro.find_element_by_xpath('//*[@id="multiCheckul"]/li[1]/div[2]/div[1]').find_element_by_tag_name(
            'input').get_attribute('id'))
        del (s[-1])
        data.update(ID=''.join(md5(s)))
        # 全部答案
        value_li = bro.find_element_by_id('multiCheckul').find_elements_by_tag_name('li')
        value_list = []
        for value_ in value_li:
            value_list.append(value_.get_attribute('textContent'))
        list1 = bro.find_element_by_id('answerText').find_elements_by_tag_name('p')
        # 正确答案
        answer_list = []
        for list_1 in list1:
            answer_list.append(list_1.get_attribute('textContent'))
        a_list = []
        for i in range(len(answer_list)):
            a_list.append(str(value_list.index(answer_list[i])))
        data.update(answer=','.join(a_list))
        print(data)
        session.post(url=ti_url, headers=headers, data=data)

    if a == 'judgeCheck':
        s = list(bro.find_element_by_xpath('//*[@id="judgeCheckul"]/li[1]/div[2]/div[1]').find_element_by_tag_name(
            'input').get_attribute('id'))
        del (s[-1])
        data.update(ID=''.join(md5(s)))
        answer_ = bro.find_element_by_id('answerText').get_attribute('textContent')
        if answer_ == '正确':
            answer_num = '1'
        if answer_ == '错误':
            answer_num = '0'
        data.update(answer=answer_num)
        print(data)
        session.post(url=ti_url, headers=headers, data=data)


if __name__ == '__main__':
    bro = webdriver.Chrome('./chromedriver.exe')
    session = requests.Session()
    LoginName = input('账号:')
    password = input('密码:')
    print("1:积极分子 800题")
    print("2:发展对象 80题")
    admin = input('选择阶段:')
    dangke_question()
    panduan()
    print('已完成')
