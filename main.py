# https://github.com/line/line-bot-sdk-python#synopsis
import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, PostbackEvent, TextSendMessage)

from bot import retrieve_line_list

app = Flask(__name__)

# https://qiita.com/shimajiri/items/cf7ccf69d184fdb2fb26
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

SHOW = 'show_line_list'
RANDOM = 'choose_station_randomly'
CENTER = 'calculate_center_station'
mode = None


@app.route("/")
def hello_world():
    return "hello world!"


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


@handler.add(PostbackEvent)
def handle_postback(event):
    global mode
    data = event.postback.data
    if data == SHOW:
        mode = SHOW
        text = '都道府県名を入力してください。'
    line_bot_api.reply_message(
        event.reply_token,
        messages=TextSendMessage(text=text))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global mode
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title='路線一覧',
                    text='都道府県の路線一覧を表示します。',
                    actions=[
                        PostbackAction(
                            label='都道府県を入力',
                            data=SHOW)]),
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

    input_text = event.message.text.strip()
    if input_text == '集合場所':
        msg = carousel_template_message
    elif mode == SHOW:
        output_text = retrieve_line_list(input_text)
        msg = TextSendMessage(text=output_text)
        mode = None
    else:
        msg = None
    if msg is not None:
        line_bot_api.reply_message(event.reply_token, messages=msg)


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
