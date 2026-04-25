import pandas as pd
from db import fetch, execute


def get_trades():
    return fetch("SELECT * FROM trades ORDER BY date")


def add_trade(ticker, qty, price, ttype, date):

    execute("""
        INSERT INTO trades (date, ticker, qty, price, type)
        VALUES (?, ?, ?, ?, ?)
    """, (date, ticker.upper(), qty, price, ttype))


def build_positions():

    trades = get_trades()

    positions = {}

    for _, t in trades.iterrows():

        tk = t["ticker"]

        if tk not in positions:
            positions[tk] = {"qty": 0, "avg": 0}

        pos = positions[tk]

        if t["type"] == "BUY":

            new_qty = pos["qty"] + t["qty"]

            if new_qty > 0:
                pos["avg"] = ((pos["qty"] * pos["avg"]) + (t["qty"] * t["price"])) / new_qty

            pos["qty"] = new_qty

        elif t["type"] == "SELL":
            pos["qty"] -= t["qty"]

    return positions