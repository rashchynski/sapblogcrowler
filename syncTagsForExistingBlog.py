import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading
import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading
import re
from datetime import datetime

from datetime import datetime

con = sl.connect('sdn.db')

failed_pages = []
update_data = []

with con:
    res = con.execute("select id, link from blog where title like '%...' LIMIT 1000")

    for row in res:
        try:
            page = requests.get('https://community.sap.com' + row[1])
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            failed_pages.append(row[1])

        soup = BeautifulSoup(page.content, 'html.parser')
        scripts_list = soup.find_all(class_="page-link lia-link-navigation lia-custom-event")

        for script_element in scripts_list:
            title = script_element.get_text().strip()

            print(str(row[0]) + '\t' + title)

            update_data.append((
                title,
                row[0]
            ))

    sql = 'update blog set title = ? where id = ?'

    with con:
        con.executemany(sql, update_data)
