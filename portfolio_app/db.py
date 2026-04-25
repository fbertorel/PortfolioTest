import sqlite3
from config import DB_NAME

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()


def init_db():

    c.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        ticker TEXT,
        qty REAL,
        price REAL,
        type TEXT
    )
    """)

    conn.commit()


def execute(query, params=()):
    c.execute(query, params)
    conn.commit()


def fetch(query):
    import pandas as pd
    return pd.read_sql(query, conn)