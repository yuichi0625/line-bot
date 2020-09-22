import os
import random

import psycopg2
from psycopg2.extras import NamedTupleCursor
from linebot.models import (
    TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, TextSendMessage, PostbackAction, ButtonsTemplate)

SHOW = 'show_line_list'
RANDOM = 'choose_station_randomly'
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


class Bot:
    def __init__(self):
        self.DATABASE_URL = os.environ.get('DATABASE_URL')
        self.PREF_EXEPTIONS = {'北海道', '青森県', '鹿児島県', '沖縄県'}
        self.LINES = list({record.line for record in self._retrieve_data("SELECT line FROM stations;")})
        self.mode = None
        self.db_lines = {}
        self.db_prefs = {}

    def _retrieve_data(self, sql):
        with psycopg2.connect(self.DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return rows

    def reply(self, text):
        # カルーセルを表示
        if text == '集合場所':
            msg = CAROUSEL_TEMPLATE
        # 路線一覧
        elif text == SHOW:
            msg = '都道府県名を入力してください。'
            self.mode = SHOW
        elif self.mode == SHOW:
            msg = self.retrieve_line_list(text)
        # ランダム
        elif text == RANDOM:
            text = '都道府県名か路線名を入力してください。'
            self.mode = RANDOM
        elif self.mode == RANDOM:
            msg = self.retrieve_random_station(text)
        # 中間地点
        if isinstance(msg, str):
            msg = TextSendMessage(text=msg)
        return msg

    def retrieve_line_list(self, pref):
        if pref in self.PREF_EXEPTIONS:
            text = 'リソースの関係で含まれていません。申し訳ありません...。'
        else:
            sql = f"SELECT line FROM stations WHERE pref = '{pref}';"
            lines = {record.line for record in self._retrieve_data(sql)}
            if lines:
                text = ''
                for line in sorted(list(lines)):
                    text += f'{line}\n'
            else:
                text = '都道府県が見つかりません。\n（「都道府県」はついていますか？）'
        self.mode = None
        return text.strip()

    def retrieve_random_station(self, pref_or_line):
        if pref_or_line in self.PREF_EXEPTIONS:
            text = 'リソースの関係で含まれていません。申し訳ありません...。'
        else:
            if pref_or_line in self.db_lines:
                db_lines = [pref_or_line]
            else:
                db_lines = [line for line in self.LINES if line.endswith(pref_or_line)]
            if len(db_lines) > 1:
                self.db_lines = set(db_lines)
                db_lines = sorted(db_lines)
                return self._create_buttons_template(
                    title='路線候補選択',
                    text='路線の候補が複数あります。正しい方を選んでください。',
                    labels=db_lines,
                    datas=db_lines)
            elif len(db_lines) == 1:
                sql = f"SELECT station FROM stations WHERE line = '{db_lines[0]}';"
            else:
                sql = f"SELECT station FROM stations WHERE pref = '{pref_or_line}';"
            stations = {record.station for record in self._retrieve_data(sql)}
            if stations:
                station = random.choice(stations)
                text = f'{station}駅！'
            else:
                text = '都道府県／路線が見つかりません。'
        self.db_lines = {}
        self.mode = None
        return text

    @staticmethod
    def _create_buttons_template(title, text, labels, datas):
        actions = [
            PostbackAction(label=label, data=data)
            for label, data in zip(labels, datas)]
        return TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title=title,
                text=text,
                actions=actions))
