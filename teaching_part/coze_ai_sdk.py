'''
这个例子描述了如何使用对话界面创始对话，调查对话状态，并在对话完成后获取消息。
'''

import os
import time
from cozepy import COZE_COM_BASE_URL
from dotenv import load_dotenv

from cozepy import Coze, TokenAuth, Message, ChatStatus  # noqa

# 加载 .env 文件
load_dotenv()

# 获取环境变量
your_coze_api_token = os.getenv("COZE_AUTH")
your_coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
your_bot_id = os.getenv("COZE_BOT_ID")
your_user_id = os.getenv("USER_ID") or f"user-{int(time.time())}"


def coze_ai_sdk(coze_api_base, coze_api_token, bot_id, user_content, user_id=None):
    # 这个是用 sdk 请求 coze ai 的方法

    if user_id is None:  # 当 user_id 没有传入时动态生成
        user_id = f"user-{int(time.time())}"

    # 校验关键环境变量
    if not coze_api_token:
        return ValueError("Missing COZE_AUTH. Please check your .env file.")
    if not bot_id or bot_id == "bot id":
        return ValueError("Invalid COZE_BOT_ID. Please check your .env file.")

    try:
        # 初始化 Coze 客户端
        coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

        # 调用 create_and_poll
        chat_poll = coze.chat.create_and_poll(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=[
                Message.build_user_question_text(user_content),
            ],
        )

        # 打印第一条消息内容
        if chat_poll.messages:
            return chat_poll.messages[0].content
        else:
            return "No messages received."

    except Exception as e:
        print(f"An error occurred: {e}")


# 执行函数
reply = coze_ai_sdk(your_coze_api_base, your_coze_api_token, your_bot_id, "你知道原神嘛")
print(reply)




# # 打印消息
# for message in chat_poll.messages:
#     print(message.content)

# # 打印 token 使用信息
# if chat_poll.chat.status == ChatStatus.COMPLETED:
#     print("Token usage:", chat_poll.chat.usage.token_count)



# import os
# import time
#
# from cozepy import COZE_COM_BASE_URL
# from dotenv import load_dotenv
#
# load_dotenv()  # 加载 .env 文件
#
# # 通过个人访问令牌或 OAuth 获取 access_token。
# # coze_api_token = os.getenv("COZE_API_TOKEN")
# coze_api_token = os.getenv("COZE_AUTH")
# # 默认访问 api.coze.com，但如果需要访问 api.coze.cn，请通过 base_url 配置访问的 API 端点
# coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
#
# from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa
#
# # 通过 access_token 初始化 Coze 客户端。
# coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)
#
# # 在 Coze 中创建一个机器人实例，从网页链接中复制最后一个数字作为机器人的 ID。
# bot_id = os.getenv("COZE_BOT_ID") or "bot id"
# # user id 用于标识用户的身份。开发者可以使用自定义业务 ID 或随机字符串。
# user_id = "user id"
#
#
# # 为了简化调用，SDK 提供了一个包装函数，用于完成非流为对话、调用状态和获取消息。开发者可以使用 create_and_poll 来简化流程。
# chat_poll = coze.chat.create_and_poll(
#     bot_id=bot_id,
#     user_id=user_id,
#     additional_messages=[
#         Message.build_user_question_text("如何学好英语"),
#     ],
# )
# for message in chat_poll.messages:
#     print(message.content, end="", flush=True)
#
# if chat_poll.chat.status == ChatStatus.COMPLETED:
#     print()
#     print("token usage:", chat_poll.chat.usage.token_count)



# # 为了简化调用，SDK 提供了一个包装函数，用于完成非流为对话、调用状态和获取消息。开发者可以使用 create_and_poll 来简化流程。
# chat_poll = coze.chat.create_and_poll(
#     bot_id=bot_id,
#     user_id=user_id,
#     additional_messages=[
#         Message.build_user_question_text("Who are you?"),  # 用户问题
#         Message.build_assistant_answer("I am Bot by Coze."),  # 机器人回答
#         Message.build_user_question_text("What about you?"), # 用户问题
#     ],
# )
# for message in chat_poll.messages:
#     print(message.content, end="", flush=True)
#
# if chat_poll.chat.status == ChatStatus.COMPLETED:
#     print()
#     print("token usage:", chat_poll.chat.usage.token_count)


# if os.getenv("RUN_STEP_BY_STEP"):
#     # 调用 coze.chat.create 方法创建对话。create 方法是非流为对话，并将返回 Chat 类。开发者应常检查对话的状态，并根据不同状态单独处理。
#     chat = coze.chat.create(
#         bot_id=bot_id,
#         user_id=user_id,
#         additional_messages=[
#             Message.build_user_question_text("Who are you?"),
#             Message.build_assistant_answer("I am Bot by Coze."),
#             Message.build_user_question_text("What about you?"),
#         ],
#     )
#
#     # 假设开发允许最多一个对话运行 10 分钟。如果超过 10 分钟，将对话取消。
#     # 并且当对话状态不是完成时，每秒调用一次对话状态。
#     # 对话完成后，获取对话中的所有消息。
#     start = int(time.time())
#     timeout = 600
#     while chat.status == ChatStatus.IN_PROGRESS:
#         if int(time.time()) - start > timeout:
#             # 超时，取消对话
#             coze.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.id)
#             break
#
#         time.sleep(1)
#         # 通过查询接口获取最新数据
#         chat = coze.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.id)
#
#     # 当对话状态转为完成时，可通过消息列表接口获取该对话中的所有消息。
#     messages = coze.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.id)
#     for message in messages:
#         print(f"role={message.role}, content={message.content}")
# else:
#     # 为了简化调用，SDK 提供了一个包装函数，用于完成非流为对话、调用状态和获取消息。开发者可以使用 create_and_poll 来简化流程。
#     chat_poll = coze.chat.create_and_poll(
#         bot_id=bot_id,
#         user_id=user_id,
#         additional_messages=[
#             Message.build_user_question_text("Who are you?"),
#             Message.build_assistant_answer("I am Bot by Coze."),
#             Message.build_user_question_text("What about you?"),
#         ],
#     )
#     for message in chat_poll.messages:
#         print(message.content, end="", flush=True)
#
#     if chat_poll.chat.status == ChatStatus.COMPLETED:
#         print()
#         print("token usage:", chat_poll.chat.usage.token_count)
