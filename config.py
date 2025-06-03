
# pip install sqlitecloud

import sqlitecloud

# Open the connection to SQLite Cloud
def conexion_BD():
    return sqlitecloud.connect("sqlitecloud://czdl3prfnz.g5.sqlite.cloud:8860/Biblioteca_GM.db?apikey=jy2XKNctf5sPhCv19XlzIphSKXwlvoQvb3mmwokjWsY")



'''
import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Data", "Biblioteca_GM.db")

def conexion_BD():
    return sqlite3.connect(DB_PATH)
'''