from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# 填写chromedriver的目录, 此处使用了相对路径(如果无法正常运行请下载chromedriver)
# chromedriver_path = Service('../public/drivers/chromedriver.exe')
chromedriver_path = Service("")  # 默认路径


def create_web():  # 打开浏览器
    options = Options()
    options.add_argument("--start-maximized")  # 启动时最大化窗口
    return webdriver.Chrome(service=chromedriver_path, options=options)  # 默认使用chromedriver的系统路径


# 创建Chrome浏览器实例
chrome = create_web()

# 打开抖音网站
chrome.get('https://www.douyin.com/')

# 每隔10秒打印"网页正在运行"
while True:
    print("网页正在运行...")
    time.sleep(10)
