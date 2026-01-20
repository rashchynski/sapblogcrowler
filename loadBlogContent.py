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

blacklist = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head',
    'input',
    'script',
    # there may be more elements you don't want, such as "style", etc.
]

with con:
    res = con.execute("select id, link from blog where wordcount is null  order by created desc  LIMIT 100")

    for index, row in enumerate(res):
        try:
            page = requests.get("https://community.sap.com" + row[1])
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            failed_pages.append(row[1])

        soup = BeautifulSoup(page.content, 'html.parser')
        scripts_list = soup.find_all(class_="lia-message-body-content")

        for script_element in scripts_list:
            text = script_element.find_all(string=True)
            output = ''

            for t in text:
                if t.parent.name not in blacklist:
                    output += '{} '.format(t)

        print(str(index) + '\t' + str(row[0]) + '\t' + str( len(output.split()) ) )

        update_data.append((
            len(output.split()),
            row[0]
        ))

    sql = 'update blog set wordcount = ? where id = ?'

    with con:
        con.executemany(sql, update_data)
