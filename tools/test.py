import os
import psycopg2
from psycopg2.extras import NamedTupleCursor


DATABASE_URL = os.environ.get('DATABASE_URL')

with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute(
            f"select station, line from stations;")
        rows = cur.fetchall()
        row = rows[0]
        print(f'row: {row}')
        print(f'row.line: {row.line}')
