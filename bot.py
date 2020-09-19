import os
import random
import re
from collections import defaultdict

import numpy as np
import psycopg2


class Bot:
    def __init__(self):
        self.spaces = '    '
        self.regex = re.compile(r'[\s,、]')
        self.database_url = os.environ.get('DATABASE_URL')

    def retrieve_data(self, sql):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return rows

    def reply_to_text(self, text):
        words = [word for word in self.regex.split(text) if word]
        if len(words) <= 1:
            reply = None
        elif words[0] in {'路線一覧', 'list', 'listo'}:
            reply = self.retrieve_line_list(words[1])
        elif words[0] in {'ランダム', 'random', 'hazarda'}:
            reply = self.retrieve_random_station(words[1:])
        elif words[0] in {'中間地点', 'center', 'centro'}:
            reply = self.retrieve_center_station()
        else:
            reply = None
        return reply

    def retrieve_line_list(self, pref):
        text = f'{pref}：\n'
        sql = f"select line from stations where pref = '{pref}';"
        lines = {line[0] for line in self.retrieve_data(sql)}
        if lines:
            lines = sorted(list(lines))
            for line in lines:
                text += f'{self.spaces}{line}\n'
        else:
            if pref in {'北海道', '青森県', '鹿児島県', '沖縄県'}:
                text += f'''
                    {self.spaces}リソース不足でありません。\n
                    {self.spaces}大変申し訳ありません...！'''
            else:
                text += f'{self.spaces}都道府県名を入れてください。'
        return text.strip()

    def retrieve_random_station(self, lines):
        text = ''
        for line in lines:
            sql = f"select station from stations where line = '{line}';"
            stations = {st[0] for st in self.retrieve_data(sql)}
            if stations:
                station = random.choice(list(stations))
                text += f'{line}：\n{self.spaces}{station}駅！\n'
        if not text:
            text += '有効な路線名を入れてください。'
        return text.strip()

    def retrieve_center_station(self):
        return




# class Bot:
#     def __init__(self):
#         self.regex = re.compile(r'[\s,、]')
#         self.word_show = '路線一覧'
#         self.word_select = 'ランダム'
#         self.word_calc = '中間'
#         with open('tools/line_stations.json', encoding='utf-8') as f:
#             self.line_stations_dict = json.loads(f.read())
#             self.line_keys = self.line_stations_dict.keys()
#             self.station_lines_dict = defaultdict(list)
#             for line, stations in self.line_stations_dict.items():
#                 for station in stations:
#                     self.station_lines_dict[station].append(line)
#         with open('tools/station_lon_lat.json', encoding='utf-8') as f:
#             self.station_lon_lat_dict = {
#                 sta: [float(n) for n in lon_lat] for sta, lon_lat in json.loads(f.read()).items()}
#             self.station_keys = self.station_lon_lat_dict.keys()
#             self.lon_lat_array = np.array(list(self.station_lon_lat_dict.values()))

#     def reply_to_text(self, text):
#         words = [word for word in self.regex.split(text) if word]
#         if words[0] == self.word_show:
#             output = self.show_line_list()
#         elif words[0] == self.word_select:
#             output = self.select_station_randomly(words[1:])
#         elif words[0] == self.word_calc:
#             output = self.calc_intermediate_stations(words[1:])
#         else:
#             output = None
#         return output

#     def show_line_list(self):
#         """「路線一覧」に対応

#         Returns:
#             str: 全路線名
#         """
#         return '\n'.join(self.line_stations_dict.keys())

#     def select_station_randomly(self, lines):
#         """「ランダム」に対応

#         Args:
#             lines (list): 入力された路線名のリスト

#         Returns:
#             str: ランダムに選択された駅名
#         """
#         # 空の場合
#         if not lines:
#             return
#         # 無効な路線名を除外
#         valid_lines = []
#         invalid_lines = []
#         for line in lines:
#             if line in self.line_keys:
#                 valid_lines.append(line)
#             else:
#                 invalid_lines.append(line)
#         # 有効な路線名がなかった場合
#         if not valid_lines:
#             return '「路線一覧」で選択可能な路線名を確認してください。'
#         # ランダムに駅名を取得
#         line = random.choice(valid_lines)
#         station = random.choice(self.line_stations_dict[line])
#         if invalid_lines:
#             print(f"{', '.join(line for line in invalid_lines)} is(are) the invalid line name(s).")
#         return f'{line}の{station}駅！'

#     def calc_intermediate_stations(self, num_stations):
#         """「中間」に対応

#         Args:
#             num_stations (list): 入力された数字と駅名のリスト
#         """
#         # 入力が2つ未満の場合
#         if len(num_stations) < 2:
#             return
#         # 数字を取得
#         num = num_stations[0]
#         if not num.isdigit():
#             return '「中間」のあとに数字を入力してください。'
#         # 無効な駅名を除外
#         valid_stations = []
#         invalid_stations = []
#         for station in num_stations[1:]:
#             if station in self.station_keys:
#                 valid_stations.append(station)
#             else:
#                 invalid_stations.append(station)
#         # 有効な駅名がなかった場合
#         if not valid_stations:
#             return '「中間」と数字のあとに有効な駅名を入力してください。'
#         # 中間地点を計算
#         mean_lon_lat = np.array(
#             [self.station_lon_lat_dict[station] for station in valid_stations]).mean(axis=0)
#         dists = np.apply_along_axis(
#             self.calc_distance, 1, self.lon_lat_array - mean_lon_lat)
#         intermediate_stations = [
#             t[1] for t in sorted(zip(dists, self.station_keys))[:int(num)]]
#         # 結果を表示
#         output = ''
#         for station in valid_stations:
#             output += f'- {station}駅\n'
#         for station in invalid_stations:
#             output += f'- {station}駅（無効）\n'
#         output += '\nの中間にある駅は、\n\n'
#         for i, station in enumerate(intermediate_stations, 1):
#             output += f"{i}. {station}駅（{', '.join(self.station_lines_dict[station])}）\n"
#         return output.strip()

#     @staticmethod
#     def calc_distance(x_y):
#         x, y = x_y
#         return np.sqrt(x**2 + y**2)
