from selenium import webdriver
import time
import pickle
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

import pandas as pd
import os


data_list = []  # 这里定义一个全局变量来存储数据

current_dir = os.path.dirname(os.path.abspath(__file__))
path_cookie = os.path.join(current_dir, "../public/other/douyin_cookie.pickle")
path_data_excel = os.path.join(current_dir, "public/excel/data.xlsx")

load_dotenv()  # 加载 .env 文件

DOUYIN_LIVE_URL = os.getenv('DOUYIN_LIVE_URL') or 'https://live.douyin.com/'
DOUYIN_URL = os.getenv('DOUYIN_URL') or 'https://www.douyin.com/'
DOUYIN_ROOM = os.getenv('DOUYIN_ROOM') or '741682777632'

COZE_BOT_ID = os.getenv('COZE_BOT_ID') or '739612312322'
COZE_AUTH = os.getenv('COZE_AUTH') or 'pat_8RRGfabcdefgs4zMD'


def create_web(headless=False):  # 初始化浏览器, 并打开
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 创建Chrome浏览器实例
    chrome = webdriver.Chrome(options=options)  # 默认使用chromedriver的系统路径

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

                        # 将新数据作为新行添加到 data_list 中
                        data_list.append([username, comment, "", ""])

                        # 打印用户名和评论
                        print(f"用户名: {username} | 评论: {comment}")

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

    global data_list  # 用于处理用户回复
    data_list = []  # 清空数据列表

    thread1.start()


if __name__ == '__main__':
    # 创建Chrome浏览器实例
    chrome = create_web(headless=False)

    # 自定义您要进入的直播间链接
    chrome.get(DOUYIN_LIVE_URL + DOUYIN_ROOM)  # 李宁直播间
    # chrome.get('https://live.douyin.com/509601340564')  # 陆教授直播间

    # 启动主程序
    main()