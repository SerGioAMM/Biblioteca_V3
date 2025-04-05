import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Data", "biblioteca.db")

def conexion_BD():
    return sqlite3.connect(DB_PATH)