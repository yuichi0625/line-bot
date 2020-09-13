# https://github.com/line/line-bot-sdk-python#synopsis
import json
import os
import random
import re

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
    line_stations_dict = json.loads(f.read())
catalog_regex = re.compile(r'集合場所一覧(?=$|。)')
station_regex = re.compile(r'集合場所は(?=\?|？)')
line_name_regex = re.compile(r'[^と].*?(?=と|で)')


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
    input_text = event.message.text
    is_catalog = bool(catalog_regex.search(input_text))
    is_station = bool(station_regex.search(input_text))
    lines = line_name_regex.findall(input_text)

    output_text = None
    if input_text in {'路線一覧', '路線一覧。'}:
        output_text = '\n'.join([line for line in line_stations_dict.keys()])
    elif is_catalog:
        output_text = extract_catalog(lines)
    elif is_station:
        output_text = extract_station(lines)

    if output_text is not None:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=output_text))


def extract_catalog(lines):
    text = ''
    if not lines:
        lines = line_stations_dict.keys()
    for line in lines:
        text += f'■{line}\n    '
        stations = line_stations_dict.get(line)
        if stations is None:
            text += '候補にありません。\n'
        else:
            text += '　'.join(stations) + '\n'
    return text.strip()


def extract_station(lines):
    if not lines:
        lines = list(line_stations_dict.keys())
    else:
        lines = [line for line in lines if line in line_stations_dict.keys()]
    if not lines:
        text = '路線を見直してください。'
    else:
        line = random.choice(lines)
        station = random.choice(line_stations_dict[line])
        text = f'{line}の{station}駅！'
    return text.strip()


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
