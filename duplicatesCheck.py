import sqlite3 as sl

con = sl.connect('sdn.db')

with con:
    res = con.execute("select count( * ) as __count, max(id), blog_id, tag_id from blog2tag group by blog_id, tag_id order by __count desc")
    # res = con.execute("select * from blog where title='Accelerating Digital Transformation with New Applications in the Cloud' order by created")

    for row in res:
        if(row[0]>1):
            print(row[1])
            #print(str(row[0]) + " " + str(row[1]) + " " + str(row[2]))
            print(",")
