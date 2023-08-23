import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading

from datetime import datetime

con = sl.connect('sdn.db')

with con:
    res = con.execute("select id, created from blog limit 10")
    update_data = []

    for row in res:
        print(  )
        #August 23, 2023
        #20230823
        #row[1]
        update_data.append((
            row[1],
            datetime.strptime(row[1], "%B %d, %Y").strftime("%Y%m%d")
        ))


sql = 'update blog set created_int = ? where id = ?'

with con:
    con.executemany(sql, update_data)