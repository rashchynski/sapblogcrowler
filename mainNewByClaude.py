import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import time
import re
import undetected_chromedriver as uc
from datetime import datetime

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

sql = 'INSERT OR IGNORE INTO blog (id, title, author, link, created ) values(?, ?, ?, ?, ?)'

insert_data = []
insert_tag_data = {}

# --- Phase 1: Load blog posts from API ---

API_URL = 'https://community.sap.com/api/2.0/search'
QUERY = (
    "SELECT id,subject,view_href,post_time,author.login "
    "FROM messages "
    "WHERE conversation.style='blog' AND depth=0 "
    "ORDER BY post_time DESC "
    "LIMIT 50"
)

cursor = None
total_loaded = 0
total_added = 0
max_pages = 50

for page_num in range(max_pages):
    try:
        params = {'q': QUERY}
        if cursor:
            params['cursor'] = cursor

        resp = requests.get(API_URL, params=params, timeout=30)
        if resp.status_code == 429:
            print(f'Rate limited on page {page_num + 1}, waiting 60s...')
            time.sleep(60)
            resp = requests.get(API_URL, params=params, timeout=30)
        elif resp.status_code != 200:
            print(f'HTTP {resp.status_code} on page {page_num + 1}, retrying...')
            time.sleep(5)
            resp = requests.get(API_URL, params=params, timeout=30)
        data = resp.json()

        if data.get('status') != 'success':
            print('API error:', data.get('message'))
            break

        items = data['data']['items']
        if not items:
            break

        for item in items:
            total_loaded += 1
            id = str(item['id'])
            title = item['subject'].replace("\ud83d", " ").replace("\ud835", " ")
            author = item.get('author', {}).get('login', '')
            link = item.get('view_href', '')
            post_time = item.get('post_time', '')

            if post_time:
                createdDateString = datetime.fromisoformat(post_time).strftime("%Y%m%d")
            else:
                createdDateString = ''

            insert_tag_data[id] = []

            if id not in existing_blogs:
                if id != '14070367' and id != '14094547':
                    total_added += 1
                    insert_data.append((
                        id,
                        title,
                        author,
                        link,
                        createdDateString
                    ))

        cursor = data['data'].get('next_cursor')
        if not cursor:
            break

        print(f'Page {page_num + 1}: loaded {len(items)} posts')
        time.sleep(1)

    except Exception as e:
        print(f'Failed on page {page_num + 1}: {e}')
        break

print(f'Total loaded: {total_loaded}, new: {total_added}')

with con:
    con.executemany(sql, insert_data)

# --- Phase 2: Load SAP managed tags via browser ---

print('Loading SAP managed tags via browser...')

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=144)

try:
    count = 0
    limit = 50

    while count < limit:
        count = count + 1
        url = 'https://community.sap.com/t5/forums/searchpage/tab/message?filter=includeBlogs&q=%22a%22&page=' + str(count) + '&sort_by=-topicPostDate&collapse_discussion=true&include_blogs=true'

        try:
            driver.get(url)
            time.sleep(8)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            scripts_list = soup.find_all(class_="lia-message-view-wrapper")

            if not scripts_list:
                print(f'Search page {count}: no results, stopping')
                break

            for script_element in scripts_list:
                title_el = script_element.find(class_='page-link lia-link-navigation lia-custom-event')
                if not title_el:
                    continue

                link = title_el.attrs.get('href', '')
                m = re.search('/ba-p/(.+?)\\?', link)
                if not m:
                    m = re.search('/ba-p/(.+?)$', link)
                if not m:
                    continue
                id = m.group(1)

                if id not in insert_tag_data:
                    insert_tag_data[id] = []

                tags_list = script_element.find(class_='custom-message-associated-product')
                if tags_list:
                    try:
                        for tag in tags_list.find_all(class_='lia-link-navigation'):
                            tag_text = tag.get_text().strip()
                            if tag_text and tag_text not in insert_tag_data[id]:
                                insert_tag_data[id].append(tag_text)
                    except:
                        pass

            print(f'Search page {count}: found {len(scripts_list)} results')

        except Exception as e:
            print(f'Search page {count} failed: {e}')

finally:
    driver.quit()

# --- Phase 3: Insert tag assignments ---

tag2blog = []
missing_tags = []

for row in insert_tag_data:
    for tag in insert_tag_data[row]:
        if tag in existing_tags:
            tag2blog.append((
                existing_tags[tag],
                row
            ))
        else:
            missing_tags.append(tag)

sql = 'INSERT OR IGNORE INTO blog2tag (tag_id, blog_id) values(?, ?)'

with con:
    res = con.executemany(sql, tag2blog)

print(f'Tag assignments: {len(tag2blog)} created, {len(missing_tags)} missing tags')
print(missing_tags)
