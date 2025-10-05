import sqlite3
db = sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT,password TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS post (username TEXT,title TEXT,caption TEXT,id TEXT,date TEXt,file BLOB)")
db.commit()