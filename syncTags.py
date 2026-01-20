import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading
import re
from datetime import datetime

def get_text(a):
    return a.get_text()


con = sl.connect('sdn.db')

existing_blogs = {}
existing_tags = {}

max_tag_id = 0

with con:
    res = con.execute("select id from blog")

    for row in res:
        existing_blogs[str(row[0])] = row[0]

    res = con.execute("select title, id from tag order by id")

    for row in res:
        existing_tags[row[0]] = row[1]
        max_tag_id = row[1]


insert_data = []
insert_tag_data = {}
update_data = []
failed_pages = []

statistic_loaded = {}
statistic_added = {}
missing_tag_assignment = {}

def load_page(count):
    try:
        page = requests.get('https://community.sap.com/t5/forums/searchpage/tab/message?filter=includeBlogs&q=%22a%22&page='  + str(count) +  '&sort_by=-topicPostDate&collapse_discussion=true&include_blogs=true')
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        failed_pages.append(count)
        return

    soup = BeautifulSoup(page.content, 'html.parser')
    scripts_list = soup.find_all(class_="lia-message-view-wrapper")

    statistic_loaded[count] = 0
    statistic_added[count] = 0

    for script_element in scripts_list:
        statistic_loaded[count] = statistic_loaded[count] + 1



        try:
            author = script_element.find(class_='lia-link-navigation lia-page-link lia-user-name-link')
            author = author.contents[0].get_text()
        except:
            author = ''

        title = script_element.find(class_='page-link lia-link-navigation lia-custom-event')

        link = title.attrs['href']
        title = title.get_text().strip()

        m = re.search('/ba-p/(.+?)\?', link)

        if m:
            id = m.group(1)

        insert_tag_data[id] = []

        #if id not in existing_blogs:
        statistic_added[count] = statistic_loaded[count] + 1
        insert_data.append((
            id,
            title,
            author,
            link

        ))

        tags_list = script_element.find(class_='custom-message-associated-product')
        try:
            tags_list = tags_list.find_all(class_='lia-link-navigation')
            for tag in tags_list:
                tag = tag.get_text().strip()
                insert_tag_data[id].append( tag )
        except :  # This is the correct syntax
            print( tags_list )



count = 0
limit = count + 50
threads = []

while count < limit:
    count = count + 1
    t1 = threading.Thread(target=load_page, args=(count,))
    t1.start()
    threads.append(t1)

for thread in threads:
    thread.join()

#with con:
    #con.executemany(sql, insert_data)

tag2blog = []

missing_tags = []
tags_to_add = []

sql = "select blog_id,tag_id from blog2tag where blog_id in ({seq})".format(seq=','.join(['?']*len(insert_data)))

blog_data = []

for element in insert_data:
    blog_data.append(element[0])

with con:
    res = con.execute(sql, blog_data)

existing_blog_to_tag = set()
for row in res:
    existing_blog_to_tag.add(str(row[0])+'-'+str(row[1]))

#for row in insert_data:
for row in insert_tag_data:
    for tag in insert_tag_data[row]:
        if tag not in existing_tags:
            max_tag_id = max_tag_id + 1

            tags_to_add.append((
                max_tag_id,
                tag
            ))

            existing_tags[tag] = max_tag_id

        _key =  str(row) + '-' + str(existing_tags[tag])

        if _key not in existing_blog_to_tag:
            tag2blog.append((
                existing_tags[tag],
                row
            ))


sql = 'INSERT INTO tag (id, title) values(?, ?)'
with con:
    res = con.executemany(sql, tags_to_add)

sql = 'INSERT INTO blog2tag (tag_id, blog_id) values(?, ?)'

with con:
    res = con.executemany(sql, tag2blog)


print(tags_to_add)

print()
print()
print()

print(tag2blog)