'''
@ project: LibrarySeats
@ file: function
@ user: 罗申申
@ email: luoshenshen@buaa.edu.cn
@ tool: PyCharm
@ time: 2021/5/24 1:44
'''
import os
import requests
import time
import browser_tools
import re
import js_code
import baidu
import timer
from aip import AipOcr

requests.packages.urllib3.disable_warnings()
requests_with_session = requests.Session()


def session_get(url, header):
    requests.adapters.DEFAULT_RETRIES = 5
    return requests_with_session.get(url=url, headers=header, allow_redirects=False, verify=False)


def floors():
    print('''
        输入：21，选二楼西阅览区
        输入：22，选二楼东阅览区
        输入：23，选二楼东电子阅览区
        输入：24，选二楼西电子阅览区
        输入：31，选三楼西电子阅览区
        输入：32，选三楼东电子阅览区
        输入：33，选三楼东阅览区
        输入：34，选三楼西阅览区
        输入：35，选三楼中阅览区
        输入：41，选四楼西电子阅览区
        输入：42，选四楼东电子阅览区
        输入：43，选四楼西阅览区
        输入：44，选四楼东阅览区
        输入：45，选四楼中阅览区
        输入：51，选五楼西阅览区
        输入：52，选五楼东阅览区
        输入：53，选五楼中阅览区
        输入：61，选六楼西阅览区
        输入：62，选六楼中阅览区
        输入：63，选六楼东阅览区
        输入：64，选六楼北阅览区
        输入：71，选七楼西阅览区
        输入：72，选七楼中阅览区
        输入：73，选七楼东阅览区
        输入：81，选八楼电子西阅览区
        输入：82，选八楼东阅览区
        输入：83，选八楼西阅览区
        输入：84，选八楼中阅览区
        输入：85，选八楼电子东阅览区
        输入：91，选九楼西阅览区
        输入：92，选九楼中阅览区
        输入：93，选九楼东阅览区
        输入：1，退出
        ''')
    floor = str(input("请选择楼层："))
    if floor == "21":
        floor = str(10073)
    elif floor == "22":
        floor = str(10065)
    elif floor == "23":
        floor = str(10071)
    elif floor == "24":
        floor = str(10072)
    elif floor == "31":
        floor = str(10080)
    elif floor == "32":
        floor = str(10081)
    elif floor == "33":
        floor = str(10082)
    elif floor == "34":
        floor = str(10083)
    elif floor == "35":
        floor = str(10084)
    elif floor == "41":
        floor = str(10085)
    elif floor == "42":
        floor = str(10086)
    elif floor == "43":
        floor = str(10087)
    elif floor == "44":
        floor = str(10088)
    elif floor == "45":
        floor = str(10089)
    elif floor == "51":
        floor = str(10090)
    elif floor == "52":
        floor = str(10091)
    elif floor == "53":
        floor = str(10092)
    elif floor == "61":
        floor = str(11019)
    elif floor == "62":
        floor = str(11033)
    elif floor == "63":
        floor = str(11040)
    elif floor == "64":
        floor = str(11300)
    elif floor == "71":
        floor = str(11054)
    elif floor == "72":
        floor = str(11061)
    elif floor == "73":
        floor = str(11068)
    elif floor == "81":
        floor = str(11075)
    elif floor == "82":
        floor = str(11096)
    elif floor == "83":
        floor = str(11117)
    elif floor == "84":
        floor = str(11131)
    elif floor == "85":
        floor = str(11138)
    elif floor == "91":
        floor = str(11082)
    elif floor == "92":
        floor = str(11103)
    elif floor == "93":
        floor = str(11124)
    elif floor == "1":
        exit(1)
    return floor


def get_floor_url(url, floor):
    return url + str(floor) + '.html&' + str(int(time.time()))


def get_tomorrow_floor_url(url, floor):
    return url + str(floor)


def get_seat(html):
    xys = re.findall('data-key="(.*)" style="left:', html)
    seats = re.findall('<em>(.*)</em>', html)
    return xys, seats


def fecth(image_name):
    options = input("输入：1，进入抢座，输入：0，预选明日:")
    if options == str(1):
        floor = floors()
        url = get_floor_url(browser_tools.floor_url, floor)
        result = session_get(url, browser_tools.layout_header)

        js_result = js_code.obtain_js(result.text)
        request_js = js_result[1]
        need_js = re.findall(r"layout/(.+?).js", request_js)
        print("选座js已获取：" + need_js[0])
        verify_code = js_code.verify_code_get(need_js[0])
        js = str(verify_code)
        print("选座js匹配验证码:" + verify_code)
        xys, seats = get_seat(result.text)
        keys = {}
        for i, j in zip(xys, seats):
            keys.update({str(j): str(i)})
        print("请选择您要抢的座位：")
        for i in keys.keys():
            if i != '' and i != '柱' and i != '窗':
                print('可选座位：', i)

        key = input("请输入选座位置：")
        seats = keys.pop(key)

        result = ''
        while '预定座位成功' not in result:

            img_url = browser_tools.img_url
            hr = session_get(img_url, header=browser_tools.tomorrow_imgs_header()).headers
            if 'Location' in hr.keys():
                img_url = hr.pop('Location')

            img = session_get(img_url, header=browser_tools.img_header()).content
            with open(image_name, 'wb') as f:
                f.write(img)
            # 识别验证码
            client = AipOcr(baidu.APP_ID, baidu.API_KEY, baidu.SECRET_KEY)
            size = os.path.getsize(image_name)

            image = baidu.get_file_content(image_name)
            client.basicAccurate(image)
            options = {}
            options["detect_direction"] = "true"
            options["probability"] = "true"
            word = client.basicAccurate(image, options)
            li = word.get('words_result')

            if 0 == len(li) or size < 1500:
                continue

            code = li[0]["words"]
            print('(o゜▽゜)o☆[BINGO!]', "\tCNN卷积神经网络自动判别验证码为：", code)
            while len(code) != 4:
                img_url = browser_tools.img_url
                hr = session_get(img_url, header=browser_tools.tomorrow_imgs_header()).headers
                if 'Location' in hr.keys():
                    img_url = hr.pop('Location')
                img = session_get(img_url, header=browser_tools.img_header()).content
                with open(image_name, 'wb') as f:
                    f.write(img)
                size = os.path.getsize(image_name)
                image = baidu.get_file_content(image_name)
                client.basicAccurate(image)
                word = client.basicAccurate(image, options)
                li = word.get('words_result')
                if 0 == len(li) or size < 1500:
                    continue
                code = li[0]["words"]
                print('(o゜▽゜)o☆[BINGO!]', "\tCNN卷积神经网络自动判别验证码为：", code)

            target_url = browser_tools.today_url + str(floor) + '&' + str(js) + '=' + str(seats) + '&yzm=' + code
            result = session_get(target_url, browser_tools.today_header).text
            print("选座动作：")
            print(target_url)
            print("选座结果：")
            print(result)
            if '预定成功' in result or '操作失败' in result:
                break

    elif options == str(0):
        floor = floors()
        url = get_floor_url(browser_tools.floor_url, floor)
        result = session_get(url, browser_tools.layout_header)

        # 获取座位坐标
        xys, seats = get_seat(result.text)
        keys = {}
        for i, j in zip(xys, seats):
            keys.update({str(j): str(i)})
        print("请选择您要抢的座位：")
        for i in keys.keys():
            if i != '' and i != '柱' and i != '窗':
                print('可选座位：', i)

        key = input("请输入选座位置：")
        seats = keys.pop(key)

        print("座位坐标已获取:", seats)
        print("开始计时选座: 开始选座,请耐心等待:")

        hour, min, sec = timer.times()
        while int(hour) < int(19 and (int(19 - hour) * 3600 + int((49 - min)) * 60 + (60 - sec)) > 0):
            print('已锁定该楼层:', key, '号座位', "准备抢座:预定时间 19:50", " 当前时间:", hour, ":", min, '继续等待',
                  (int(19 - hour) * 3600 + int((49 - min)) * 60 + (60 - sec)), '秒')
            time.sleep(0.5)
            hour, min, sec = timer.times()

        while int(min) < int(50) and (int(19 - hour) * 3600 + int((49 - min)) * 60 + (60 - sec)) > 0:
            print('已锁定该楼层:', key, '号座位', "准备抢座:预定时间 19:50", " 当前时间:", hour, ":", min, '继续等待',
                  (int(19 - hour) * 3600 + int((49 - min)) * 60 + (60 - sec)), '秒')
            time.sleep(0.5)
            hour, min, sec = timer.times()

        # 最后一次刷新
        tomorrow_result = session_get(browser_tools.tomorrow, browser_tools.get_tomorrow_header())

        # 获取js验证
        js_result = js_code.obtain_js(tomorrow_result.text)
        request_js = js_result[1]
        need_js = re.findall(r"layout/(.+?).js", request_js)
        verify_code = js_code.verify_code_get(need_js[0])
        js = str(verify_code)
        client = AipOcr(baidu.APP_ID, baidu.API_KEY, baidu.SECRET_KEY)

        while 1:
            #获取验证码链接
            img_url = browser_tools.img_url
            hr = session_get(img_url, header=browser_tools.tomorrow_imgs_header()).headers
            if 'Location' in hr.keys():
                img_url = hr.pop('Location')

            #下载验证码
            img = session_get(img_url, header=browser_tools.img_header(floor)).content
            with open(image_name, 'wb') as f:
                f.write(img)

            #识别验证码
            size = os.path.getsize(image_name)
            image = baidu.get_file_content(image_name)
            client.basicAccurate(image)
            options = {}
            options["detect_direction"] = "true"
            options["probability"] = "true"
            word = client.basicAccurate(image, options)
            li = word.get('words_result')

            #判断合法性
            if len(li) == 0 or size < 1500:
                continue
            code = li[0]["words"]
            if len(code) != 4:
                continue
            print('(o゜▽゜)o☆[BINGO!]', "\tCNN卷积神经网络自动判别验证码为：", code)
            # 各种安全已经验证，开始抢座
            target_url = browser_tools.tomorrow_url + str(floor) + '&' + str(js) + '=' + str(seats) + '&yzm=' + code
            result = session_get(target_url, browser_tools.today_header).text
            print("选座结果:",result)
            if '成功' in result or '失败' in result or '满' in result:
                exit(0)
