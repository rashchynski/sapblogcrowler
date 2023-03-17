import sqlite3 as sl

con = sl.connect('sdn.db')

with con:
    res = con.execute("select count( * ) as __count, title from blog group by title order by __count")
    # res = con.execute("select * from blog where title='Accelerating Digital Transformation with New Applications in the Cloud' order by created")

    for row in res:
        if(row[0]>2):
            print(row)