import time
import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading
import re
from datetime import datetime


try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")

# to search

con = sl.connect('sdn.db')

existing_blogs = {}


to_num   = 14049869
from_num = 14049724


with con:
    res = con.execute("select id from blog where id > ?", [from_num])

    for row in res:
        existing_blogs[str(row[0])] = row[0]

my_list = []
while from_num < to_num:
    from_num = from_num + 1
    if str(from_num) not in existing_blogs:
        my_list.append(  str(from_num) )


    if len(my_list) == 10:
        numbers = " OR ".join(my_list)
        print(numbers)
        query = numbers + " site:https://community.sap.com"
        for j in search(query, tld="co.in", num=10, stop=10, pause=2):
            print(j)
        time.sleep(5)
        my_list = []




