from selenium import webdriver
import time
import pickle
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# 填写chromedriver的目录, 此处使用了相对路径(如果无法正常运行请下载chromedriver)
# chromedriver_path = Service('../public/drivers/chromedriver.exe')
chromedriver_path = Service("")  # 默认路径

current_dir = os.path.dirname(os.path.abspath(__file__))
path_cookie = os.path.join(current_dir, "../public/other/douyin_cookie.pickle")

load_dotenv()  # 加载 .env 文件

DOUYIN_LIVE_URL = os.getenv('DOUYIN_LIVE_URL') or 'https://live.douyin.com/'
DOUYIN_URL = os.getenv('DOUYIN_URL') or 'https://www.douyin.com/'
DOUYIN_ROOM = os.getenv('DOUYIN_ROOM') or '741682777632'


def create_web(headless=False):  # 初始化浏览器, 并打开

    # 创建Chrome浏览器实例
    chrome = webdriver.Chrome(service=chromedriver_path)  # 默认使用chromedriver的系统路径

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


# print(f"加载的 Cookie 文件路径: {path_cookie}")  # 打印 cookie 文件路径
# 创建Chrome浏览器实例
chrome = create_web(headless=False)

chrome.get(DOUYIN_LIVE_URL + DOUYIN_ROOM)  # 李宁直播间

# 每隔10秒打印"网页正在运行"
while True:
    print("已经登录抖音--网页正在运行...")
    time.sleep(10)
