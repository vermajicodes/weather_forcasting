# pip install mysql
# pip install mysql-connector-python

import mysql
import mysql.connector as sql 

db = sql.connect(
    host = "localhost",
    user = "root",
    password = "12345",
    use_pure = True
)   

cr = db.cursor()    
cr.execute("show databases")
for i in cr:
    print(i)