import os
import psycopg2
from psycopg2.extras import DictCursor


DATABASE_URL = os.environ.get('DATABASE_URL')

with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("select line_name from stations;")
        rows = cur.fetchall()
        print(rows)
