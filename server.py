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
    def get(self, date_pattern):
        con = sl.connect('sdn.db')
        print(date_pattern)
        with con:
            res = con.execute("SELECT count(*) as __count, created  FROM blog where created like ? group by created  order by __count desc", [(date_pattern)] )
            data = res.fetchall()

        return jsonify( data )

class ListBlogByDate(Resource):
    def get(self, date):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM blog where created = ?", [(date)] )
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class ListCreate(Resource):
    def get(self, title):
        con = sl.connect('sdn.db')
        sql = 'INSERT INTO list (title) values(?)'
        with con:
            con.executemany(sql, [(title)] )

class ListContent(Resource):
    def get(self, list_id):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM blog inner join where created = ?", [(date)] )
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )

class AddToList(Resource):
    def get(self, blog_id, list_id):
        con = sl.connect('sdn.db')
        sql = 'INSERT INTO blog2list (blog_id, list_id) values(?)'
        with con:
            con.executemany(sql, [(blog_id, list_id)] )

class RemoveFromList(Resource):
    def get(self, blog_id, list_id):
        con = sl.connect('sdn.db')
        sql = 'INSERT INTO blog2list (blog_id, list_id) values(?)'
        with con:
            con.executemany(sql, [(blog_id, list_id)] )

class Lists(Resource):
    def get(self):
        con = sl.connect('sdn.db')
        con.row_factory = sqlite3.Row
        with con:
            res = con.execute("SELECT * FROM list")
            data = res.fetchall()

        return jsonify( [dict(ix) for ix in data] )


api.add_resource(BlogCountByDatePattern, '/blog/created/count/<date_pattern>')
api.add_resource(ListBlogByDate, '/blog/list/<date>')

api.add_resource(ListCreate, '/list/create/<title>')
api.add_resource(ListContent, '/list/<list_id>')
api.add_resource(Lists, '/list')

api.add_resource(AddToList,  '/list/add/<list_id>/<blog_id>')
api.add_resource(RemoveFromList,  '/list/remove/<id>')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, extra_files=extra_files)


# http://127.0.0.1:5000//blog/created/count/February%201%252023