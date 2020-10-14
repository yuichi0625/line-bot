import argparse
import csv
import os
import re

# 以下の記事を参考に作成
# https://rowingfan.hatenablog.jp/entry/2018/09/10/174500


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv_date', default='20200619', help='csvファイルの日付を選択')
    parser.add_argument('-s', '--sql_path', default='insert_into_stations.sql', help='保存するsqlファイルのパス')
    args = parser.parse_args()

    # 駅データ.jpから、取得した県名・路線名・駅名のcsvファイルを確認
    pref_path = 'pref.csv'
    line_path = f'line{args.csv_date}free.csv'
    station_path = f'station{args.csv_date}free.csv'
    assert os.path.exists(pref_path), f'{pref_path}が見つかりません。'
    assert os.path.exists(line_path), f'{line_path}が見つかりません。'
    assert os.path.exists(station_path), f'{station_path}が見つかりません。'

    # 県名ファイルから、コードと名前の対応を取得
    with open(pref_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        pref_cd_idx = header.index('pref_cd')
        pref_name_idx = header.index('pref_name')
        pref_dict = {}
        for row in reader:
            pref_dict[row[pref_cd_idx]] = row[pref_name_idx]

    # 路線名ファイルから、コードと名前の対応を取得
    with open(line_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        line_cd_idx = header.index('line_cd')
        line_name_idx = header.index('line_name')
        line_dict = {}
        for row in reader:
            line_dict[row[line_cd_idx]] = row[line_name_idx]

    # 駅名ファイルから、駅の情報を取得
    regex = re.compile(r'[【（(].+[)）】]|\s')
    with open(station_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        station_name_idx = header.index('station_name')
        line_cd_idx = header.index('line_cd')
        pref_cd_idx = header.index('pref_cd')
        lon_idx = header.index('lon')
        lat_idx = header.index('lat')
        stations = []
        stations_append = stations.append
        for row in reader:
            station_name = regex.sub('', row[station_name_idx])
            line_name = regex.sub('', line_dict[row[line_cd_idx]])
            pref_name = pref_dict[row[pref_cd_idx]]
            lon = row[lon_idx]
            lat = row[lat_idx]
            info = f"('{pref_name}','{line_name}','{station_name}',{lon},{lat}),\n"
            # HerokuのHobby-devでは10,000件までしかレコードが登録できないため、
            # 日本の端から2道県ずつ外して合わせています。
            if pref_name not in {'北海道', '青森県', '鹿児島県', '沖縄県'}:
                stations_append(info)
        # 重複をなくす
        stations = list(set(stations))
        stations[-1] = stations[-1].replace(',\n', ';')

    # sqlファイルに書き出す
    with open(args.sql_path, 'w', encoding='utf-8') as f:
        f.write('insert into stations (pref,line,station,lon,lat) values\n')
        f.writelines(stations)


if __name__ == '__main__':
    main()
