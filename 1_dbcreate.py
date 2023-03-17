import sqlite3 as sl

con = sl.connect('sdn.db')

with con:
    con.execute("""
        CREATE TABLE list (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            title TEXT
        );
    """)