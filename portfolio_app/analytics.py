import pandas as pd
import numpy as np
import yfinance as yf

from engine import get_trades, build_positions


def get_price(ticker):
    try:
        return yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
    except:
        return None


# =========================
# EQUITY CURVE (ROBUST)
# =========================
def equity_curve():

    trades = get_trades()

    if trades.empty:
        return pd.DataFrame(columns=["date", "value"])

    trades["date"] = pd.to_datetime(trades["date"])

    dates = pd.date_range(trades["date"].min(), pd.Timestamp.today())

    curve = []

    for d in dates:

        snapshot = trades[trades["date"] <= d]

        positions = {}

        for _, t in snapshot.iterrows():

            tk = t["ticker"]

            if tk not in positions:
                positions[tk] = 0

            positions[tk] += t["qty"] if t["type"] == "BUY" else -t["qty"]

        value = 0

        for tk, qty in positions.items():
            price = get_price(tk)
            if price:
                value += qty * price

        curve.append([d, value])

    return pd.DataFrame(curve, columns=["date", "value"])


# =========================
# RISK (VOLATILITY)
# =========================
def risk_by_asset():

    trades = get_trades()

    out = {}

    for tk in trades["ticker"].unique():

        try:
            data = yf.Ticker(tk).history(period="1y")["Close"]

            ret = data.pct_change().dropna()

            out[tk] = float(ret.std() * np.sqrt(252))

        except:
            out[tk] = None

    return out


# =========================
# BENCHMARK
# =========================
def benchmark():

    sp = yf.Ticker("^GSPC").history(period="1y")["Close"]

    return sp / sp.iloc[0] * 100