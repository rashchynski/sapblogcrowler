import requests
from bs4 import BeautifulSoup
import sqlite3 as sl
import sqlite3
import threading
import json
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask import Flask, render_template
from flask_cors import CORS
from os import path, walk

extra_dirs = ['webapp', ]
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in walk(extra_dir):
        for filename in files:
            filename = path.join(dirname, filename)
            if path.isfile(filename):
                extra_files.append(filename)

app = Flask(__name__, static_folder='webapp')
cors = CORS(app)
api = Api(app)

class Hello(Resource):
    def get(self):
        return jsonify({'message': 'hello world'})

    def post(self):
        data = request.get_json()  # status code
        return jsonify({'data': data}), 201

class BlogCountByDatePattern(Resource):
    def get(self, date):
        con = sl.connect('sdn.db')
        with con:
            res = con.execute("SELECT count(*) as __count, created  FROM blog where created like ? group by created  order by created desc", [(date)] )
            data = res.fetchall()

        return jsonify( data )

class ListBlogByTag(Resource):
    def get(self, tag):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT title, created, author, link, blog_id FROM BlogWithTags where tag_id = ? order by created desc limit 200", [tag])
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )


class ListBlogByDate(Resource):
    def get(self, date):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT id, title, author, created, likes, comments, link, id as blog_id, wordcount FROM blog where created = ?", [(date)] )
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class MarkTagAsFavourite(Resource):
    def get(self, tag_id):
        con = sl.connect('sdn.db')
        sql = 'update tag set isFavourite = 1 where id = ?'

        with con:
            con.execute(sql, [tag_id])

class UnMarkTagAsFavourite(Resource):
    def get(self, tag_id):
        con = sl.connect('sdn.db')
        sql = 'update tag set isFavourite = 0 where id = ?'

        with con:
            con.execute(sql, [tag_id])




class FavouriteTags(Resource):
    def get(self):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * from tag where isFavourite = 1")
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class Tag(Resource):
    def get(self, tag_id):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * from tag where id = ?", [(tag_id)] )
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class AddToList(Resource):
    def get(self, list_id, blog_id):
        con = sl.connect('sdn.db')
        sql = 'INSERT INTO blog2list (blog_id, list_id) values(?)'
        with con:
            con.executemany(sql, [blog_id, list_id])

class ListCreate(Resource):
    def get(self, title):
        con = sl.connect('sdn.db')
        sql = 'INSERT INTO list (title) values(?)'
        with con:
            con.executemany(sql, [(title)] )

class PurgeListContent(Resource):
    def get(self, list_id):
            con = sl.connect('sdn.db')
            sql = 'delete from  blog2list  where list_id = ?'
            with con:
                con.executemany(sql, [(list_id)])
class ListContent(Resource):
    def get(self, list_id):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM BlogsInList where list_id = ? order by created desc", [list_id])
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )



class BlogSearch(Resource):
    def get(self, search):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT id, title, author, created, likes, comments, link, id as blog_id FROM blog where title like ? or id = ? order by created desc", [search, search])
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class BlogByAuthor(Resource):
    def get(self, author):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT id, title, author, created, likes, comments, link, id as blog_id FROM blog where author = ? order by created desc", [author])
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class BlogTags(Resource):
    def get(self, blog_id):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM BlogWithTags where blog_id = ?", [blog_id])
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )


class Read(Resource):
    def get(self, list_id, blog_id):
        con = sl.connect('sdn.db')
        sql = 'INSERT INTO read (blog_id) values(?)'
        with con:
            con.executemany(sql, [(blog_id)] )

class AddToList(Resource):
    def get(self, list_id, blog_id, user_id=None):
        con = sl.connect('sdn.db')
        if user_id:
            sql = 'INSERT INTO blog2list (list_id, blog_id, user_id) values(?, ?, ?)'
            with con:
                con.executemany(sql, [(list_id, blog_id, user_id)] )
        else:
            sql = 'INSERT INTO blog2list (list_id, blog_id) values(?, ?)'
            with con:
                con.executemany(sql, [(list_id, blog_id)] )

class RemoveFromList(Resource):
    def get(self, list_id, blog_id):
        con = sl.connect('sdn.db')
        sql = 'delete from  blog2list  where list_id = ? and blog_id = ?'
        with con:
            con.executemany(sql, [(list_id, blog_id)] )

class Tags(Resource):
    def get(self):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM countByTag order by title")
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )


class Robinhood(Resource):
    def get(self):
        file_path = 'c:\\Users\\12062\\value.txt'  # Replace with the actual path to your file

        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return file_content
class Favorites(Resource):
    def get(self):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM BlogsInList where list_id = 1")
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class Lists(Resource):
    def get(self):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM BlogsInList")
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )


api.add_resource(BlogCountByDatePattern,    '/blog/created/count/<date>')
api.add_resource(ListBlogByDate,            '/blog/list/date/<date>')
api.add_resource(ListBlogByTag,             '/blog/list/tag/<tag>')
api.add_resource(ListCreate,                '/list/create/<title>')
api.add_resource(ListContent,               '/list/<list_id>')
api.add_resource(PurgeListContent,           '/list/purge/<list_id>')
api.add_resource(Lists,                     '/list')
api.add_resource(AddToList,                 '/list/add/<list_id>/<blog_id>', '/list/add/<list_id>/<blog_id>/<user_id>')
api.add_resource(RemoveFromList,             '/list/remove/<list_id>/<blog_id>')

api.add_resource(BlogTags,                 '/blog/tags/<blog_id>')

api.add_resource(BlogSearch,                 '/blog/search/<search>')
api.add_resource(BlogByAuthor,                 '/blog/author/<author>')
api.add_resource(MarkTagAsFavourite, '/tag/list/favourite/<tag_id>')
api.add_resource(UnMarkTagAsFavourite, '/tag/list/favourite/remove/<tag_id>')

api.add_resource(FavouriteTags, '/tag/list/favourite')

api.add_resource(Tag, '/tag/<tag_id>')


api.add_resource(Read,             '/blog/read/<blog_id>')

api.add_resource(Favorites,                 '/favorites')

api.add_resource(Robinhood,                 '/robinhood')

#api.add_resource(Tags,                      '/tags')

# api.add_resource(AddToList,  '/list/add/<list_id>/<blog_id>')
# api.add_resource(RemoveFromList,  '/list/remove/<id>')


if __name__ == '__main__':
    app.run(host='10.18.52.68', port=5000, debug=False, extra_files=extra_files)

    #app.run(host='10.247.131.42', port=5000, debug=False, extra_files=extra_files)

    #app.run(host='10.18.56.134', port=5000, debug=False, extra_files=extra_files)

# http://127.0.0.1:5000//blog/created/count/February%201%252023