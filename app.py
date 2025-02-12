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
import logging


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
    LocationMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
    UserSource,
    RoomSource,
    GroupSource,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    PostbackEvent,
    BeaconEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    MulticastRequest,
    BroadcastRequest,
    TextMessage,
    ApiException,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    TemplateMessage,
    FlexMessage,
    Emoji,
    QuickReply,
    QuickReplyItem,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    ErrorResponse
)
import stop_loss_calculator
app = Flask(__name__)
from dotenv import load_dotenv

#加載 .env 文件中的環境變數
load_dotenv()

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




@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("call back Error hahaha")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    user_message = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if user_message=="Hello":
            replyMessage = "Fuck"
        elif user_message.startswith('設定停損點'):
            replyMessage="請輸入股票代碼及買進價格,Ex:2330/1000"
        elif '/' in user_message:
            stock_code, buy_price = user_message.split('/')
            replyMessage = f"買進價格:{buy_price}"
            try:
                buy_price = float(buy_price)
                stop_loss_five_percent, stop_loss_four_percent = stop_loss_calculator.calculate_stop_loss(
                    buy_price)

                ma_data = stop_loss_calculator.calculate_moving_averages(
                    stock_code, buy_price=buy_price)

                current_5ma_diff = ma_data['5MA_diff'].iloc[-1]
                current_10ma_diff = ma_data['10MA_diff'].iloc[-1]
                current_20ma_diff = ma_data['20MA_diff'].iloc[-1]
                current_60ma_diff = ma_data['60MA_diff'].iloc[-1]

                message = f"停損價格（-5%）：{stop_loss_five_percent}\n"
                message += f"停損價格（-4%）：{stop_loss_four_percent}\n"
                message += f"5MA與買進價格的差距百分比：{current_5ma_diff:.2f}%\n"
                message += f"10MA與買進價格的差距百分比：{current_10ma_diff:.2f}%\n"
                message += f"20MA與買進價格的差距百分比：{current_20ma_diff:.2f}%\n"
                message += f"60MA與買進價格的差距百分比：{current_60ma_diff:.2f}%"

                replyMessage = message
            except ValueError:
                replyMessage = "輸入格式錯誤，請輸入股票代碼及買進價格，例如：2330/670"
        else:
            replyMessage = "查詢不到"

        messages = [TextMessage(text=replyMessage)]
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )
        except Exception as e:
            print(f"Error in replyMessage_with_http_info: {e}")


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)