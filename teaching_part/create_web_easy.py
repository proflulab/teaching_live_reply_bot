import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 填写chromedriver的目录, 此处使用了相对路径(如果无法正常运行请下载chromedriver)
# chromedriver_path = Service('../public/drivers/chromedriver.exe')

chromedriver_path = Service("")  # 默认路径

chrome = webdriver.Chrome(service=chromedriver_path)
chrome.get("https://www.douyin.com/")

time.sleep(10)
