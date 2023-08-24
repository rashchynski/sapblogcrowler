import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading

from datetime import datetime

con = sl.connect('sdn.db')

with con:
    res = con.execute("select id, created from blog")
    update_data = []

    for row in res:
        print()
        # August 23, 2023
        # 20230823
        # row[1]
        update_data.append((
            datetime.strptime(row[1], "%B %d, %Y").strftime("%Y%m%d"),
            row[0]
        ))

sql = 'update blog set created = ? where id = ?'

with con:
    con.executemany(sql, update_data)
