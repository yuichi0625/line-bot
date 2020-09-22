# https://github.com/line/line-bot-sdk-python#synopsis
import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, MessageAction, URIAction, PostbackEvent, TextSendMessage)

app = Flask(__name__)

# https://qiita.com/shimajiri/items/cf7ccf69d184fdb2fb26
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


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
    data = event.postback.data
    if data == 'show_line_list':
        text = '都道府県名を入力してください。'
    line_bot_api.reply_message(
        event.reply_token,
        messages=TextSendMessage(text=text))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='路線一覧',
                    text='各都道府県の路線一覧を表示',
                    actions=[
                        PostbackAction(
                            label='都道府県を入力',
                            # display_text='postback text1',
                            data='show_line_list')]),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='this is menu2',
                    text='description2',
                    actions=[
                        PostbackAction(
                            label='postback2',
                            display_text='postback text2',
                            data='action=buy&itemid=2'),
                        MessageAction(
                            label='message2',
                            text='message text2'),
                        URIAction(
                            label='uri2',
                            uri='http://example.com/2')])]))

    print(event)

    line_bot_api.reply_message(
        event.reply_token,
        messages=carousel_template_message)


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
