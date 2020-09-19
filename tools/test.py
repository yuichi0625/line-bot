import os
import psycopg2


DATABASE_URL = os.environ.get('DATABASE_URL')

with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM stations')
        rows = cur.fetchall()
        print(rows)
