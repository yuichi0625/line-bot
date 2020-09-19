import os
import psycopg2


DATABASE_URL = os.environ.get('DATABASE_URL')
pref = '香川県'

with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(
            f"select line from stations where pref={pref};")
        rows = cur.fetchall()
        print(rows)
