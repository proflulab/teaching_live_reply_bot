'''
Author: 杨仕明 shiming.y@qq.com
Date: 2024-12-19 21:23:08
LastEditors: 杨仕明 shiming.y@qq.com
LastEditTime: 2024-12-19 21:35:01
FilePath: /teaching_live_reply_bot/teaching_part/coze_ai_sdk.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# 

"""
This example describes how to use the chat interface to initiate conversations,
poll the status of the conversation, and obtain the messages after the conversation is completed.
"""

import os  # noqa

# Get an access_token through personal access token oroauth.
coze_api_token = "pat_3tFpehraILy0ZxvG5kruoM2BTRzSXKDTyR72YEFk2tWieK2tjgteKiT67P1n8tJ6"

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url="https://api.coze.cn/")

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = "7448987567515156495"
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "76547575"

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.chat.stream(
    bot_id=bot_id, user_id=user_id, additional_messages=[Message.build_user_question_text("How are you?")]
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        message = event.message
        print(f"role={message.role}, content={message.content}")
