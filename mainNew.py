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

with con:
    res = con.execute("select id from blog")

    for row in res:
        existing_blogs[str(row[0])] = row[0]

    res = con.execute("select title, id from tag")

    for row in res:
        existing_tags[row[0]] = row[1]

sql = 'INSERT INTO blog (id, title, author, link, created ) values(?, ?, ?, ?, ?)'

insert_data = []
insert_tag_data = {}
update_data = []
failed_pages = []

statistic_loaded = {}
statistic_added = {}
missing_tag_assignment = {}

def check_date_format(date_string, format_string):
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False

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

        created = script_element.find(class_='lia-message-post-date lia-component-post-date lia-component-message-view-widget-post-date')
        created = created.find(class_='DateTime')

        try:
            created = created.contents[1].attrs['title'].strip()
        except:
            created = created.find(class_='local-date')
            created = created.contents[0].getText().strip()

        if check_date_format(created, "\u200e%Y %b %d %H:%M %p"):
            createdDateString = datetime.strptime(created, "\u200e%Y %b %d %H:%M %p").strftime("%Y%m%d")

        if check_date_format(created, "\u200e%Y %b %d"):
            createdDateString = datetime.strptime(created, "\u200e%Y %b %d").strftime("%Y%m%d")

        #print(createdDateString)

        try:
            author = script_element.find(class_='lia-link-navigation lia-page-link lia-user-name-link')
            author = author.contents[0].get_text()
        except:
            author = ''

        title = script_element.find(class_='page-link lia-link-navigation lia-custom-event')



        link = title.attrs['href']
        title = title.get_text().strip().replace("\ud83d", " ")
        title = title.replace("\ud835", " ")


        m = re.search('/ba-p/(.+?)\?', link)
        if m:
            id = m.group(1)

##        print( created   + '\t' + author   + '\t' +  title  + '\t' + link + '\t' + id )


        insert_tag_data[id] = []

        if id not in existing_blogs:
            if id != '14070367' and id != '14094547':
                statistic_added[count] = statistic_loaded[count] + 1
                insert_data.append((
                    id,
                    title,
                    author,
                    link,
                    createdDateString
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

print(insert_data)
with con:
    con.executemany(sql, insert_data)

tag2blog = []

missing_tags = []

#for row in insert_data:
for row in insert_tag_data:
    for tag in insert_tag_data[row]:
        if tag in existing_tags:
            tag2blog.append((
                existing_tags[tag],
                row
            ))
        else:
            missing_tags.append(tag)


sql = 'INSERT INTO blog2tag (tag_id, blog_id) values(?, ?)'

with con:
    res = con.executemany(sql, tag2blog)


print(missing_tags)