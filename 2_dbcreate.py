import sqlite3 as sl

con = sl.connect('sdn.db')

with con:
    con.execute("""
        CREATE TABLE blog2list (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            blog_id INTEGER NOT NULL,
            list_id INTEGER NOT NULL
        );
    """)