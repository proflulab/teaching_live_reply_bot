from selenium import webdriver
import time
import pickle
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
path_cookie = os.path.join(current_dir, "../public/other/douyin_cookie.pickle")
path_data_excel = os.path.join(current_dir, "public/excel/data.xlsx")

load_dotenv()  # 加载 .env 文件

DOUYIN_LIVE_URL = os.getenv('DOUYIN_LIVE_URL') or 'https://live.douyin.com/'
DOUYIN_URL = os.getenv('DOUYIN_URL') or 'https://www.douyin.com/'
DOUYIN_ROOM = os.getenv('DOUYIN_ROOM') or '741682777632'


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
        text_element.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"发送消息时发生错误: {e}")


def main():  # 启动双线程
    while True:
        send_message("111")
        print("已经发送信息至抖音")
        time.sleep(10)


if __name__ == '__main__':
    # 创建Chrome浏览器实例
    chrome = create_web(headless=False)

    # 自定义您要进入的直播间链接
    chrome.get(DOUYIN_LIVE_URL + DOUYIN_ROOM)  # 李宁直播间
    # chrome.get('https://live.douyin.com/509601340564')  # 陆教授直播间

    # 启动主程序
    main()