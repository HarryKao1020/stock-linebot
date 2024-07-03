# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)
configuration = Configuration(
    access_token=channel_access_token
)
# Custom ApiClient to force utf-8 encoding
# class Utf8ApiClient(ApiClient):
#     def __init__(self, configuration):
#         super().__init__(configuration)
#         self.rest_client.pool_manager.connection_pool_kw['headers'] = {
#             'Content-Type': 'application/json; charset=utf-8'
#         }


print("hahaha123")
print("handler",handler)
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("Body:",body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("call back Error hahaha")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    print("event:",event)
    user_message = event.message.text
    print("event message",user_message)
    

    with ApiClient(configuration) as api_client:
        print("start reply message")
        line_bot_api = MessagingApi(api_client)
        print("line_bot_api:",line_bot_api)
        messages = [TextMessage(text=event.message.text.encode("utf-8").decode("utf-8"))]
        print("messages:", messages)
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='Hello user')]
                )
            )
        except Exception as e:
            print(f"Error in reply_message_with_http_info: {e}")


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)