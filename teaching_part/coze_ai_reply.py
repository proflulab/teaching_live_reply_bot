from dotenv import load_dotenv
import json
from urllib import request, error
import os

load_dotenv()  # 加载 .env 文件

COZE_BOT_ID = os.getenv('COZE_BOT_ID')
COZE_AUTH = os.getenv('COZE_AUTH')


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

    # Convert data to JSON string and encode it
    data = json.dumps(data).encode()

    # Create a Request object
    req = request.Request(url, data=data, headers=headers, method='POST')

    try:
        # Send the request and get the response
        with request.urlopen(req) as response:
            response_data = response.read()
            # Decode JSON response
            response_json = json.loads(response_data.decode())
            # print(response_json)  打印演示内容

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


response = main_req("你知道ai训练营吗", COZE_AUTH, COZE_BOT_ID)
print(response)
