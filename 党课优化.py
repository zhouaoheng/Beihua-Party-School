# coding=gbk
# @Time : 2021-04-07 22:03
# @Author : ZAH
# @File : �����Ż�.py
# @Software : PyCharm
import json
import time

import requests
from lxml import etree
from retry import retry
import re
import random
import os
import xlrd
import hashlib
import base64


url = 'http://wldx.beihua.edu.cn/m/Exam/Student/Login#'
get_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/StudyOnline'
post_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/SaveStudentRecord'
my_study_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/MyStudy'
LoginOut_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/LoginOut'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/69.0.3493.3 Safari/537.36 '
}

def md5(pw):
    hl = hashlib.md5()
    hl.update(pw.encode(encoding='utf-8'))
    return hl.hexdigest()

def jiami(pw):
    return base64.b64encode(pw.encode('utf-8'))

def study_time():
    while 1:
        R = session.get(url=my_study_url, headers=headers)
        if R.status_code == 200:
            break
        print("��������!\n")
    my_study_page = R.text
    tree = etree.HTML(my_study_page)
    study = tree.xpath('//div[@class="item-title label text-align-r"]/text()')
    print('����:' + study[0] + '\n')
    print('�Ա�:' + study[1] + '\n')
    print('ѧ��:' + study[2] + '\n')
    print('ѧϰʱ��:' + study[3] + '\n')
    return study[3]


@retry(exceptions=(IndexError, ConnectionError), delay=2)
def skip_class():
    s_time = study_time()
    s_time = re.findall('\d+', s_time, re.S)[0]
    s_time = int(s_time)
    StudyOnline_page = session.get(url=get_url, headers=headers).text
    tree = etree.HTML(StudyOnline_page)
    onclick_list = tree.xpath('//div[@class="list-block media-list"]/ul/li/a/@onclick')
    name_list = tree.xpath('//div[@class="item-title"]/text()')
    ex = "'(.*?)'"
    onclick_list = re.findall(ex, str(onclick_list), re.S)
    num = len(name_list)
    print('�γ��б�:\n')
    for class_num in range(0, num):
        print(str(class_num) + ':' + name_list[class_num])
    input_num = int(input("������Ҫˢ�Ŀγ̺�:"))
    # input_num = 0
    onclick = onclick_list[input_num]
    study_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/Course?courseID=' + str(onclick)
    page_text = session.get(url=study_url, headers=headers).text
    tree = etree.HTML(page_text)
    li_list = tree.xpath('//*[@id="content"]/li/a/@onclick')
    id_list = re.findall(ex, str(li_list), re.S)
    for id in id_list[::-1]:
        if s_time >= input_time:
            print('����' + str(input_time) + '���ӣ�ˢ�ν���')
            break
        print(time.strftime('\n'+'%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print('�γ�ID:' + id)
        video_time = str(random.randrange(20, 30, 1))
        print('�γ�ʱ��:' + video_time)
        data = {
            'ChapterID': str(id),
            'StudyTime': video_time
        }
        session.post(url=post_url, headers=headers, data=data)
        s_time = int(video_time) + s_time
        print('��ǰ��ʱ��:' + str(s_time))
        # 1S �ӳ�
        # time.sleep(1)


if __name__ == '__main__':
    session = requests.Session()
    LoginName = input('�˺�:')
    password = input('����:')
    input_time = int(input("������Ҫˢ��ʱ��:"))
    while(1):
        login_data = {
            'LoginName': LoginName,
            'password': jiami(password)
        }
        print(time.strftime('\n'+'%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print('���ڳ��Ե�¼:' + str(LoginName))
        r = session.post(url=url, headers=headers, data=login_data)
        a = json.loads(r.text)
        if a['Success'] == 0:
            print("ѧ�Ż����벻��ȷ��")
            LoginName = input('�˺�:')
            password = input('����:')
        if a['Success'] == -1:
            print("��ǰ��¼�����϶࣬���Ժ��¼��")
        if a['Success'] == 2:
            print("�˺ű�������ɾ����")
            LoginName = input('�˺�:')
            password = input('����:')
        if a['Success'] == 1:
            print("��¼�ɹ���")
            break;
        time.sleep(2)

    skip_class()
    print('ȫ�����')
    #�˳���½
    session.post(url=LoginOut_url, headers=headers)
    os.system('pause')
