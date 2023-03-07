import sqlite3 as sl




con = sl.connect('sdn.db')

with con:
    con.execute("""
        CREATE TABLE blog (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            created INTEGER,
            likes INTEGER,
            comments INTEGER
        );
    """)