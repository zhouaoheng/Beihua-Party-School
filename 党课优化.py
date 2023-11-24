# coding=gbk
# @Time : 2021-04-07 22:03
# @Author : ZAH
# @File : 党课优化.py
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

url = 'https://wldx.beihua.edu.cn/m/Exam/Student/Login#'
get_url = 'https://wldx.beihua.edu.cn/m/Exam/Student/StudyOnline'
post_url = 'https://wldx.beihua.edu.cn/m/Exam/Student/SaveStudentRecord'
my_study_url = 'https://wldx.beihua.edu.cn/m/Exam/Student/MyStudy'
LoginOut_url = 'https://wldx.beihua.edu.cn/m/Exam/Student/LoginOut'
ResetPassword_url = "https://wldx.beihua.edu.cn/m/Exam/Student/ResetPassword"

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


def resetPassword(oldPassword, Password):
    data = {
        'oldPassword': jiami(oldPassword),
        'Password': jiami(Password)
    }
    while 1:
        R = session.post(url=ResetPassword_url, headers=headers, data=data)
        print("正在修改密码")
        if R.status_code == 200:
            print("已修改密码为:" + Password)
            break


# 获取视频ID
def getVideoID(id):
    video_url = "https://wldx.beihua.edu.cn/m/Exam/Student/startStudy?chapterID="+id
    video_text = session.get(url=video_url, headers=headers).text
    videoInfo = etree.HTML(video_text).xpath("//video/source/@src")[0]
    video_id = videoInfo.split("/")[-1].split(".")[0]
    return video_id


def study_time():
    while 1:
        R = session.get(url=my_study_url, headers=headers)
        if R.status_code == 200:
            break
        print("正在重试!\n")
    my_study_page = R.text
    tree = etree.HTML(my_study_page)
    study = tree.xpath('//div[@class="item-title label text-align-r"]/text()')
    print('姓名:' + study[0] + '\n')
    print('性别:' + study[1] + '\n')
    print('学号:' + study[2] + '\n')
    print('学习时间:' + study[3] + '\n')
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
    print('课程列表:\n')
    for class_num in range(0, num):
        print(str(class_num) + ':' + name_list[class_num])
    # input_num = int(input("请输入要刷的课程号:"))
    input_num = 0
    onclick = onclick_list[input_num]
    study_url = 'http://wldx.beihua.edu.cn/m/Exam/Student/Course?courseID=' + str(onclick)
    page_text = session.get(url=study_url, headers=headers).text
    tree = etree.HTML(page_text)
    li_list = tree.xpath('//*[@id="content"]/li/a/@onclick')
    id_list = re.findall(ex, str(li_list), re.S)
    for id in id_list[::-1]:
        if s_time >= input_time:
            print('超过' + str(input_time) + '分钟，刷课结束')
            break
        print(time.strftime('\n' + '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print('课程ID:' + id)
        video_time = str(random.randrange(20, 30, 1))
        print('课程时间:' + video_time)
        data = {
            'ChapterID': str(id),
            'VideoID': getVideoID(id),
            'StudyTime': video_time
        }
        session.post(url=post_url, headers=headers, data=data)
        s_time = int(video_time) + s_time
        print('当前总时长:' + str(s_time))
        # 1S 延迟
        # time.sleep(1)


if __name__ == '__main__':
    session = requests.Session()
    LoginName = input('账号:').strip()
    password = input('密码:').strip()

    # 不输入密码则为默认密码
    if password.strip() is None:
        password = "@BHdx1234"

    input_time = 1440
    # input_time = int(input("请输入要刷的时长:")).strip()

    while (1):
        login_data = {
            'LoginName': LoginName,
            'password': jiami(password)
        }
        print(time.strftime('\n' + '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print('正在尝试登录:' + str(LoginName))
        r = session.post(url=url, headers=headers, data=login_data)
        a = json.loads(r.text)
        if a['Success'] == 0:
            print("学号或密码不正确！")
            LoginName = input('账号:').strip()
            password = input('密码:').strip()
        if a['Success'] == -1:
            print("当前登录人数较多，请稍后登录！")
        if a['Success'] == 2:
            print("账号被锁定或删除！")
            LoginName = input('账号:').strip()
            password = input('密码:').strip()
        if a['Success'] == 3:
            resetPassword(password, "Aa123456@")
            break
        if a['Success'] == 1:
            print("登录成功！")
            break

        time.sleep(2)

    skip_class()
    print('全部完成')
    # 退出登陆
    session.post(url=LoginOut_url, headers=headers)
    os.system('pause')
