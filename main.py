from selenium import webdriver
import time
import pickle
import threading
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
from urllib import request, error
import threading

import pandas as pd
import os

import re

data_list = []  # 这里定义一个全局变量来存储数据

# 填写chromedriver的目录, 此处使用了相对路径(如果无法正常运行请下载chromedriver)
# chromedriver_path = Service('../public/drivers/chromedriver.exe')
chromedriver_path = Service("")  # 默认路径

current_dir = os.path.dirname(os.path.abspath(__file__))
path_cookie = os.path.join(current_dir, "public/other/douyin_cookie.pickle")
path_data_excel = os.path.join(current_dir, "public/excel/data.xlsx")

load_dotenv()  # 加载 .env 文件

DOUYIN_LIVE_URL = os.getenv('DOUYIN_LIVE_URL') or 'https://live.douyin.com/'
DOUYIN_URL = os.getenv('DOUYIN_URL') or 'https://www.douyin.com/'
DOUYIN_ROOM = os.getenv('DOUYIN_ROOM') or '741682777632'

COZE_BOT_ID = os.getenv('COZE_BOT_ID') or '739612312322'
COZE_BOT_JUDGMENT_ID = os.getenv('COZE_BOT_JUDGMENT_ID') or '739612312322'
COZE_AUTH = os.getenv('COZE_AUTH') or 'pat_8RRGfabcdefgs4zMD'


def create_web(headless=False):  # 初始化浏览器, 并打开
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 创建Chrome浏览器实例
    chrome = webdriver.Chrome(service=chromedriver_path, options=options)  # 默认使用chromedriver的系统路径

    # 打开抖音网站
    chrome.get(DOUYIN_URL)

    # 调用加载 Cookie 文件
    if os.path.exists(path_cookie):
        # 加载 Cookie 文件
        load_cookies(chrome, path_cookie)
    else:
        # 保存 Cookie 文件到本地
        save_cookies(chrome, path_cookie)

        # 加载 Cookie 文件
        load_cookies(chrome, path_cookie)

    return chrome


def save_cookies(driver, cookie_path):  # 保存 Cookie 文件
    # 保存 Cookie 文件

    # 等待用户手动登录
    time.sleep(1)
    input("登入抖音账号后，请输入任意键继续...")
    time.sleep(0.3)

    # 保存 Cookies 到文件
    with open(cookie_path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, cookie_path):  # 加载 Cookie 文件
    # 加载 Cookie 文件
    with open(cookie_path, 'rb') as file:
        cookies_list = pickle.load(file)

    for cookie in cookies_list:
        driver.add_cookie(cookie)


def remove_non_bmp_characters(text):  # 删除特殊符号的符号，以防万一发送不出去报错
    return ''.join(c for c in text if ord(c) <= 0xFFFF)


def send_message(message):  # 向抖音直播间发送信息
    """发送指定的消息并按下 Enter 键"""
    try:
        # 等待文本区域元素加载并找到
        text_element = WebDriverWait(chrome, 10).until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@class="webcast-chatroom___textarea"]'))
        )
        text_element.clear()
        text_element.send_keys(message)
        time.sleep(0.5)

        # 按下 Enter 键发送消息
        # text_element.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"发送消息时发生错误: {e}")


def is_robot_reply(comment, max_check_count):  # 不讲！判断是否是机器人发送的回复
    """
    判断是否是机器人发送的回复，防止信息被录入。

    :param comment: 当前评论内容
    :param max_check_count: 最多检查的行数
    :return: 如果是机器人发送的回复，返回 True；否则返回 False
    """
    if len(data_list) > 1:
        latest_non_empty_comment = None

        # 从下往上遍历 data_list，最多检查 max_check_count 行
        for i, row in enumerate(reversed(data_list)):
            if i >= max_check_count:
                break
            if row[3]:  # 如果当前行的第4项不为空
                latest_non_empty_comment = remove_non_bmp_characters(row[3])
                # print(f"Checking row: {i+1}, Comment: {latest_non_empty_comment}")  # 调试输出
                break  # 找到第一个非空值项后，跳出循环

        # 如果找到了非空值项，则与 comment 的前10个字符进行比较
        if latest_non_empty_comment:
            # print(f"Comparing: {latest_non_empty_comment[:10]} with {comment[:10]}")  # 调试输出
            if comment[:10] == latest_non_empty_comment[:10]:
                # print(f"Latest row number: {len(data_list)} - Skipping")  # 打印最新行数
                return True  # 是机器人发送的回复

    return False  # 不是机器人发送的回复


def monitor_screen():  # 获取用户在抖音直播间发送的信息
    last_data_id = None  # 用于存储上一个 `data-id`

    try:
        while True:
            try:
                # 确保页面元素加载完成
                web_text_elements = WebDriverWait(chrome, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div.webcast-chatroom___item.webcast-chatroom___enter-done'))
                )

                if web_text_elements:
                    # 提取最新的元素
                    latest_element = web_text_elements[-1]

                    # 获取当前元素的 `data-id`
                    current_data_id = latest_element.get_attribute('data-id')

                    # 如果 `data-id` 与上一个相同，则跳过
                    if current_data_id == last_data_id:
                        time.sleep(0.2)  # 等待一段时间后再次检查
                        continue

                    # 更新 `last_data_id`
                    last_data_id = current_data_id

                    try:
                        # 尝试获取用户名
                        username_element = latest_element.find_element(By.CSS_SELECTOR, '.u2QdU6ht')
                        username_text = username_element.text

                        # 尝试获取评论
                        comment_element = latest_element.find_element(By.CSS_SELECTOR, '.WsJsvMP9')
                        comment = comment_element.text

                        # 如果子项有 lEfJhurR 类别，则跳过,这里防止送礼物的信息被录入
                        if comment_element.find_elements(By.CSS_SELECTOR, '.lEfJhurR'):
                            continue

                        # 检查用户名最后一个字符是否为 `：`，如果不是则跳过，防止直播间进入消息提示
                        if not username_text.endswith('：'):
                            continue
                        # 去掉用户名中的最后一个字符 `：`
                        username = username_text[:-1]  # 移除最后一个字符 `：`

                        # 这段代码用于判断是否是我的机器人发送的回复，防止信息被录入
                        if is_robot_reply(comment, 4):  # 前面一个变量是用户评论，后面是最多向上查找数量
                            continue  # 跳过该条记录

                        # 将新数据作为新行添加到 data_list 中
                        data_list.append([username, comment, "", ""])

                        # 打印用户名和评论
                        # print(f"用户名: {username} | 评论: {comment}")
                    except Exception as inner_e:
                        # 如果在尝试获取用户名或评论时出错，继续到下一个元素
                        print("## 提取信息时发生错误，可能是没找到类别，不用在意，可以查看这段代码的位置进行调试 ##")  # 防止一些非信息元素出bug
                        inner_e = inner_e  # 这段变量没有任何用处，只是防止报错，如果要调试，可以删除这段代码
                        # print(f"提取信息时发生错误: {inner_e}")  # 调试使用
                        continue

                else:
                    print("没有找到发言元素")

            except Exception as e:
                print(f"监控公屏时发生错误: {e}")

            # 等待一段时间后再次检查
            time.sleep(1)  # 可以根据需要调整检查间隔

    except Exception as e:
        print(f"监控公屏时发生错误: {e}")


def main_req(user_text, user_token, bot_id):  # 向coze机器人客服发送信息
    url = "https://api.coze.cn/open_api/v2/chat"
    headers = {
        "Authorization": "Bearer" + user_token,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    data = {
        "conversation_id": "123",
        "bot_id": bot_id,
        "user": "29032201862555",
        "query": user_text,
        "stream": False
    }

    # 转换数据为 JSON 字符串并编码
    data = json.dumps(data).encode()

    # 创建请求对象
    req = request.Request(url, data=data, headers=headers, method='POST')

    try:
        # 发送请求并获取响应
        with request.urlopen(req) as response:
            response_data = response.read()
            # Decode JSON response
            response_json = json.loads(response_data.decode())

            # 遍历消息列表，找到第一个类型为 'answer' 的消息
            for message in response_json.get('messages', []):
                if message.get('type') == 'answer':
                    # 返回该消息的内容
                    return message.get('content', '内容为空').strip()  # 删除首尾空格

    except error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        response_body = e.read()
        print(f"Response body: {response_body.decode()}")
    except error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return '请求失败'  # 请求失败时的返回内容


def run_main_thread():  # 主运行部分
    data_list_round_count = 0  # 这是运行到的行数值

    try:
        while True:
            if data_list:
                # 如果 data_list 不是空的，处理数据

                if len(data_list) > data_list_round_count:
                    # 调用用户综合数据，user_typ_complex是发送给coze机器人的，username是用户姓名，comment是用户评论
                    user_name, comment = user_typ_transfer(data_list_round_count)
                    print(f"用户名: {user_name} | 评论: {comment}")

                    # 判断是否是问句
                    first_three_chars = main_req(comment, COZE_AUTH, COZE_BOT_JUDGMENT_ID)
                    print(first_three_chars)

                    # 检查 result 是否不等于 "非问句"
                    if first_three_chars == "是问句":
                        # 获取机器人回复并在前加上@user_name
                        result = f"@{user_name}, {main_req(comment, COZE_AUTH, COZE_BOT_ID)}"

                        clean_message = remove_non_bmp_characters(result)  # 删除特殊符号
                        # 发送信息到抖音
                        send_message(clean_message)  # 去除特殊符号在发送

                        # 将用户信息以及机器人回复储存到data_list
                        data_list[data_list_round_count][2:4] = [first_three_chars, result]

                        # 将用户信息以及机器人回复储存到Excel
                        append_to_excel(path_data_excel, user_name, comment, first_three_chars, result)
                        print(result)

                    else:
                        # 将用户信息以及机器人回复储存到data_list
                        data_list[data_list_round_count][2] = first_three_chars

                        # 将用户信息以及机器人回复储存到Excel
                        append_to_excel(path_data_excel, user_name, comment, first_three_chars, "")

                    data_list_round_count += 1

            else:
                # 如果 data_list 为空，可以选择暂停一段时间再检查
                time.sleep(1)  # 暂停 1 秒

    except KeyboardInterrupt:
        print("程序被中断")


def user_typ_transfer(data_list_round_count):  # 获取并且转换列表内的信息
    # 检查 data_list 是否为空
    if not data_list:
        return "数据列表为空"

    # 访问第一行的资料
    data_row = data_list[data_list_round_count]
    user_name = data_row[0]  # 用户名字
    comment = data_row[1]  # 用户发送的信息

    # 返回格式化的字符串
    return user_name, comment


def append_to_excel(data_file_path, username, user_comment, judgment_question, bot_reply):  # 储存信息到Excel
    # file_path是文件名称，username是抖音用户名称，user_comment是用户评论，bot_reply是机器人回复

    # 检查文件是否存在
    if os.path.exists(data_file_path):
        # 如果文件存在，从 Excel 中加载数据
        df = pd.read_excel(data_file_path, engine='openpyxl')
    else:
        # 如果文件不存在，创建一个新的 DataFrame
        df = pd.DataFrame(columns=['用户名', '用户评论', '判断问句', '客服回复'])

    # 新数据
    new_data = {
        '用户名': [username],
        '用户评论': [user_comment],
        '判断问句': [judgment_question],
        '客服回复': [bot_reply]
    }

    # 将新数据转换为 DataFrame
    new_df = pd.DataFrame(new_data)

    # 将新数据追加到 DataFrame
    df = pd.concat([df, new_df], ignore_index=True)

    # 将 DataFrame 保存到 Excel 文件
    df.to_excel(data_file_path, index=False, engine='openpyxl')


def main():  # 启动双线程
    # 启动线程
    thread1 = threading.Thread(target=monitor_screen, name="MonitorScreen")
    thread2 = threading.Thread(target=run_main_thread, name="MainThread")

    global data_list  # 用于处理用户回复
    data_list = []  # 清空数据列表

    thread1.start()
    thread2.start()


if __name__ == '__main__':
    # 创建Chrome浏览器实例
    chrome = create_web(headless=False)

    # 自定义您要进入的直播间链接
    chrome.get(DOUYIN_LIVE_URL + DOUYIN_ROOM)  # 李宁直播间
    # chrome.get('https://live.douyin.com/509601340564')  # 陆教授直播间

    # 启动主程序
    main()
