# https://github.com/line/line-bot-sdk-python#synopsis
import json
import os
import random

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler)
from linebot.exceptions import (
    InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage)

app = Flask(__name__)

# https://qiita.com/shimajiri/items/cf7ccf69d184fdb2fb26
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

with open('stations.json', encoding='utf-8') as f:
    line_stations = json.loads(f.read())


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(f'event: {event}')
    input_text = event.message.text
    if input_text.endswith('集合場所一覧'):
        pass
    elif input_text.endswith('集合場所は？') or input_text.endswith('集合場所は?'):
        line = random.choice(list(line_stations.keys()))
        station = random.choice(line_stations[line])
        output_text = f'{station}集合'
    else:
        return
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=output_text))


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
