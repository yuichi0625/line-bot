import argparse
import csv
import json
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--line_csv', default='line20200619free.csv')
    parser.add_argument('-s', '--station_csv', default='station20200619free.csv')
    parser.add_argument('-u', '--lines_config', default='lines_config.json')
    args = parser.parse_args()

    # returns {line_name: line_cd}
    with open(args.line_csv, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_line_cd = header.index('line_cd')
        idx_line_name = header.index('line_name')
        line_name_cd_dict = {}
        for row in reader:
            line_name_cd_dict[row[idx_line_name]] = row[idx_line_cd]

    # returns {line_cd: [[station_name, lon, lat], ...]}
    with open(args.station_csv, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_station_name = header.index('station_name')
        idx_line_cd = header.index('line_cd')
        idx_lon = header.index('lon')
        idx_lat = header.index('lat')
        line_cd_station_info_dict = defaultdict(list)
        for row in reader:
            line_cd_station_info_dict[row[idx_line_cd]].append(
                [row[idx_station_name], row[idx_lon], row[idx_lat]])

    # returns {line_name: line name defined by user}
    with open(args.lines_config, encoding='utf-8') as f:
        lines_config_dict = json.loads(f.read())

    line_stations_dict = defaultdict(list)
    station_lon_lat_dict = {}
    for line_name, line_name_by_user in lines_config_dict.items():
        line_cd = line_name_cd_dict.get(line_name)
        if line_cd:
            station_infos = line_cd_station_info_dict[line_cd]
            for station_name, lon, lat in station_infos:
                line_stations_dict[line_name_by_user].append(station_name)
                station_lon_lat_dict[station_name] = [lon, lat]

    with open('line_stations.json', 'w', encoding='utf-8') as f:
        json.dump(line_stations_dict, f, ensure_ascii=False)

    with open('station_lon_lat.json', 'w', encoding='utf-8') as f:
        json.dump(station_lon_lat_dict, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
