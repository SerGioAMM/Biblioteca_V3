import sqlite3

'''
def conexion_BD():
    conexion = sqlite3.connect('Data/Biblioteca.db')
    conexion.row_factory = sqlite3.Row

    return conexion
'''

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Data", "Biblioteca.db")

def conexion_BD():
    print("Ruta BD:", DB_PATH)  # O loguearlo con logging
    return sqlite3.connect(DB_PATH)




