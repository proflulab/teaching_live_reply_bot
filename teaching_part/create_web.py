from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def create_web():  # 打开浏览器
    options = Options()
    options.add_argument("--start-maximized")  # 启动时最大化窗口
    return webdriver.Chrome(options=options)  # 默认使用chromedriver的系统路径


# 创建Chrome浏览器实例
chrome = create_web()

# 打开抖音网站
chrome.get('https://www.douyin.com/')

# 每隔10秒打印"网页正在运行"
while True:
    print("网页正在运行...")
    time.sleep(10)
