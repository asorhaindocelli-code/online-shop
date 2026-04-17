import sqlite3
import os
from flask import Flask, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, 'shop.db')

def get_db_connection():
    connection =  sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

conn = get_db_connection()
cursor = conn.cursor()

conn.commit()
conn.close()