import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading
import re
from datetime import datetime

con = sl.connect('sdn.db')

existing_blogs_and_tags = {}
existing_blogs = {}
failed_pages = []
loaded_tags = {}
existing_tags = {}
tags_to_add = []
max_tag_id = 0

insert_data = {}

with con:
    res = con.execute("select title, id from tag order by id")

    for row in res:
        existing_tags[row[0]] = row[1]
        max_tag_id = row[1]

    res = con.execute("select blog_id, tag_id, link from BlogWithTags order by blog_id desc LIMIT 100 ")

    for row in res:
        existing_blogs_and_tags[str(row[0]) + "/" + str(row[1])] = (row[0], row[1], row[2])
        existing_blogs[str(row[0])] = row[0]


def load_page(existing_blogs):
    try:
        if existing_blogs[2].startswith("https://blogs.sap.com"):
            url = existing_blogs[2]
        else:
            url = "https://blogs.sap.com" + existing_blogs[2]

        page = requests.get(url)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        failed_pages.append((existing_blogs[0], existing_blogs[1]))
        return

    soup = BeautifulSoup(page.content, 'html.parser')
    tag_sections = soup.find_all(class_="lia-list-standard-inline")

    for tag_section in tag_sections:

        tags_list = tag_section.find_all(class_='lia-link-navigation lia-custom-event')
        for tag in tags_list:
            tag = tag.get_text().strip()

            if tag not in existing_tags:
                max_tag_id = max_tag_id + 1

                tag_id = max_tag_id

                tags_to_add.append((
                    max_tag_id,
                    tag
                ))
            else:
                tag_id = existing_tags[tag]

            blogAssignemnt = str(existing_blogs[0]) + "/" + str(tag_id)

            if blogAssignemnt not in existing_blogs_and_tags:
                insert_data[blogAssignemnt] = ( existing_blogs[0], tag_id )


threads = []

for existing_blogs in existing_blogs_and_tags:
    t1 = threading.Thread(target=load_page, args=(existing_blogs_and_tags[existing_blogs],))
    t1.start()
    threads.append(t1)

for thread in threads:
    thread.join()



print( tags_to_add )
print()
print()
print()
print()

for _insert_ in insert_data:
    print("insert into blog2tag (blog_id, tag_id) values " + str(insert_data[_insert_]) + ";")


