import sqlite3

'''

def conexion_BD():
    conexion = sqlite3.connect('Data/Biblioteca_GM.db')
    return conexion




'''

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Data", "Biblioteca_GM.db")

def conexion_BD():
    return sqlite3.connect(DB_PATH)





#    conexion.row_factory = sqlite3.Row
