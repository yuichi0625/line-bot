import os
import random
import re
from collections import defaultdict

import numpy as np
import psycopg2
from psycopg2.extras import NamedTupleCursor
from linebot.models import (
    TemplateSendMessage, CarouselTemplate, CarouselColumn, TextSendMessage, PostbackAction, ButtonsTemplate)


class Bot:
    def __init__(self):
        self.DATABASE_URL = os.environ.get('DATABASE_URL')
        self.PREF_EXCEPTIONS = {'北海道', '青森県', '鹿児島県', '沖縄県'}
        self.PREF_EXCEPTION_MSG = 'リソースの関係で含まれていません。申し訳ありません...。'
        self.in_operation = False

    def reply_to_message(self, msg):
        return NotImplementedError

    def reply_to_postback(self, pb):
        return NotImplementedError

    def _retrieve_data(self, sql):
        with psycopg2.connect(self.DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return rows

    @staticmethod
    def _create_buttons_template(alt_text, title, text, labels, datas):
        actions = [PostbackAction(label=label, data=data) for label, data in zip(labels, datas)]
        return TemplateSendMessage(
            alt_text=alt_text,
            template=ButtonsTemplate(
                title=title, text=text, actions=actions))


class LineListDisplayer(Bot):
    def __init__(self):
        super().__init__()


class RandomlyStationExtractor(Bot):
    def __init__(self):
        super().__init__()


class CenterStationCalculator(Bot):
    def __init__(self):
        super().__init__()
        self.regex = re.compile(r'[\s,、]')
        self.coords = []
        self.duplicated = {}

    def reply_to_message(self, str_stations):
        stations = [st for st in self.regex.split(str_stations) if st]
        for station in stations:
            sql = f"SELECT pref, lon, lat FROM stations WHERE station = '{station}';"
            records = self._retrieve_data(sql)
            pref_coords = defaultdict(list)
            for record in records:
                pref_coords[record.pref].append([record.lon, record.lat])
            pref_coord = {pref: np.mean(lon_lats, axis=0) for pref, lon_lats in pref_coords.items()}
            if len(pref_coord) > 1:
                self.duplicated[station] = pref_coord
            elif len(pref_coord) == 1:
                self.coords.append(list(pref_coord.values())[0])
        return self.reply_to_postback(None)

    def reply_to_postback(self, station_pref):
        if station_pref is not None:
            station, pref = station_pref.split('+')
            self.coords.append(self.duplicated.pop(station)[pref])
        if self.duplicated:
            station = list(self.duplicated.keys())[0]
            prefs = sorted(list(self.duplicated[station].keys()))
            return self._create_buttons_template(
                alt_text='駅名重複確認',
                title='駅名重複確認',
                text=f'{station}駅が複数の都道府県に存在します。正しい方を選んでください。',
                labels=prefs,
                datas=[f'{station}+{pref}' for pref in prefs])
        else:
            coord = np.mean(self.coords, axis=0)
            print(coord)
