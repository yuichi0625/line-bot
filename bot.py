import os

import psycopg2
from psycopg2.extras import NamedTupleCursor

DATABASE_URL = os.environ.get('DATABASE_URL')
PREF_EXEPTIONS = {'北海道', '青森県', '鹿児島県', '沖縄県'}


def _retrieve_data(sql):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return rows


def retrieve_line_list(pref):
    if pref in PREF_EXEPTIONS:
        text = 'リソースの関係で含まれていません。\n申し訳ありません...。'
    else:
        sql = f"SELECT line FROM stations WHERE pref = '{pref}';"
        lines = {record.line for record in _retrieve_data(sql)}
        if lines:
            text = ''
            for line in lines:
                text += f'    {line}\n'
        else:
            text = '都道府県が見つかりません。\n（「都道府県」も忘れずにつけてください。）'
    return text.strip()
