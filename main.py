# https://github.com/line/line-bot-sdk-python#synopsis
import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, PostbackEvent, TextSendMessage)

from bot import (
    LineListDisplayer, RandomlyStationExtractor, CenterStationCalculator)

app = Flask(__name__)

# https://qiita.com/shimajiri/items/cf7ccf69d184fdb2fb26
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

list_displayer = LineListDisplayer()
random_extractor = RandomlyStationExtractor()
center_calculator = CenterStationCalculator()

DISPLAY = 'display_line_list'
RANDOM = 'extract_station_randomly'
CENTER = 'calculate_center_station'
CAROUSEL_TEMPLATE = TemplateSendMessage(
    alt_text='Carousel template',
    template=CarouselTemplate(
        columns=[
            CarouselColumn(
                title='路線一覧',
                text='都道府県の路線一覧を表示します。',
                actions=[
                    PostbackAction(
                        label='都道府県を入力',
                        data=DISPLAY)]),
            CarouselColumn(
                title='駅名選択',
                text='指定した都道府県／路線からランダムに一駅選びます。',
                actions=[
                    PostbackAction(
                        label='都道府県／路線を入力',
                        data=RANDOM)]),
            CarouselColumn(
                title='中間地点',
                text='指定した駅の中間地点にある駅を算出します。',
                actions=[
                    PostbackAction(
                        label='駅を入力',
                        data=CENTER)])]))


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
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = None
    text = event.message.text.strip()
    if text == '集合場所':
        msg = CAROUSEL_TEMPLATE
    elif list_displayer.in_operation:
        msg = list_displayer.reply_to_message(text)
    elif center_calculator.in_operation:
        msg = center_calculator.reply_to_message(text)
    if isinstance(msg, str):
        msg = TextSendMessage(text=msg)
    if msg is not None:
        line_bot_api.reply_message(event.reply_token, messages=msg)


@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data == DISPLAY:
        msg = '都道府県名を入力してください。'
        list_displayer.in_operation = True
    elif data == RANDOM:
        msg = '都道府県名か路線名を入力してください。'
        random_extractor.in_operation = True
    elif data == CENTER:
        msg = '駅名を入力してください。'
        center_calculator.in_operation = True
    elif random_extractor.in_operation:
        msg = random_extractor.reply_to_postback(data)
    elif center_calculator.in_operation:
        msg = center_calculator.reply_to_postback(data)
    if isinstance(msg, str):
        msg = TextSendMessage(text=msg)
    line_bot_api.reply_message(event.reply_token, messages=msg)


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
