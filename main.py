import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import threading

def get_text(a):
    return a.get_text()


con = sl.connect('sdn.db')

existing_blogs = {}
existing_tags = {}

with con:
    res = con.execute("select title, id from blog")

    for row in res:
        existing_blogs[row[0]] = row[1]

    res = con.execute("select title, id from tag")

    for row in res:
        existing_tags[row[0]] = row[1]

sql = 'INSERT INTO blog (title, author, link, created, likes, comments) values(?, ?, ?, ?, ?, ?)'

insert_data = []
insert_tag_data = {}
update_data = []
failed_pages = []

statistic_loaded = {}
statistic_added = {}

def load_page(count):
    try:
        page = requests.get('https://blogs.sap.com/page/' + str(count) + '/')
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        failed_pages.append(count)
        return

    soup = BeautifulSoup(page.content, 'html.parser')
    scripts_list = soup.find_all(class_="dm-contentListItem")

    statistic_loaded[count] = 0
    statistic_added[count] = 0

    for script_element in scripts_list:
        statistic_loaded[count] = statistic_loaded[count] + 1

        title = script_element.find(class_='dm-contentListItem__title')
        title = title.find('a')
        link = title.attrs['href']
        title = title.get_text()

        created = script_element.find(class_='dm-user__date')
        created = created.contents[2].get_text().strip()

        author = script_element.find(class_='dm-user__heading')
        author = author.find('a')
        author = author.get_text()

        counts = script_element.find_all(class_='dm-contentListItem__metadataNumber')
        comments = counts[0].get_text()
        likes = counts[1].get_text()

        all_tags = script_element.find_all(class_='dm-tags__list-item')
        all_tags = map(get_text, all_tags)

        if title not in existing_blogs:
            statistic_added[count] = statistic_loaded[count] + 1

            insert_tag_data[title] = all_tags

            insert_data.append((
                title,
                author,
                link,
                created,
                comments,
                likes
            ))

    if statistic_loaded[count] < 10:
        print( statistic_loaded[count] )

    if divmod(count, 100)[1] == 0:
        print("Loaded " + str(count))


count = 0
limit = count + 20
threads = []

while count < limit:
    count = count + 1
    t1 = threading.Thread(target=load_page, args=(count,))
    t1.start()
    threads.append(t1)


sql = "select title, id from blog where title in ({seq})".format(seq=','.join(['?']*len(insert_data)))

blog_data = []

for element in insert_data:
    blog_data.append(element[0])

with con:
    res = con.execute(sql, blog_data)

tag2blog = []

missing_tags = []

for row in res:
    for tag in insert_tag_data[row[0]]:
        if tag in existing_tags:
            tag2blog.append((
                existing_tags[tag],
                row[1]
            ))
        else:
            missing_tags.append((tag, row[1]))


sql = 'INSERT INTO blog2tag (tag_id, blog_id) values(?, ?)'

with con:
    res = con.executemany(sql, tag2blog)

print(failed_pages)

print()

print(missing_tags)

print()

for statistic_key in statistic_loaded.keys():
    if statistic_loaded[statistic_key] < 10:
        print( statistic_loaded[statistic_key] )

print()

for statistic_key in statistic_added.keys():
    if statistic_added[statistic_key] > 0:
        print( statistic_added[statistic_key] )


print()