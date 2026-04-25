import streamlit as st
from datetime import datetime

from db import init_db, execute
from engine import add_trade, build_positions
from analytics import equity_curve, risk_by_asset, benchmark, get_price

import pandas as pd

init_db()

st.set_page_config(layout="wide")
st.title("📊 Portfolio Pro (Production Style)")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Trades",
    "Portfolio",
    "Equity",
    "Risk",
    "Benchmark"
])

# =========================
# TRADES
# =========================
with tab1:

    st.subheader("Agregar trade")

    ticker = st.text_input("Ticker")
    qty = st.number_input("Qty", min_value=0.0)
    price = st.number_input("Price", min_value=0.0)
    ttype = st.selectbox("Type", ["BUY", "SELL"])

    if st.button("Guardar"):
        add_trade(ticker, qty, price, ttype, datetime.now().isoformat())
        st.success("OK")

    st.divider()

    st.subheader("Historial")

    st.dataframe(
        pd.read_sql("SELECT * FROM trades ORDER BY date DESC", init_db.__globals__["conn"]),
        use_container_width=True
    )

# =========================
# PORTFOLIO
# =========================

    # version vieja
# with tab2:

#     positions = build_positions()

#     rows = []

#     total_cost = 0
#     total_value = 0

#     for t, p in positions.items():

#         price = get_price(t)
#         if not price:
#             continue

#         cost = p["qty"] * p["avg"]
#         value = p["qty"] * price

#         pnl = value - cost
#         pnl_pct = (pnl / cost) * 100 if cost else 0

#         total_cost += cost
#         total_value += value

#         rows.append([t, p["qty"], p["avg"], price, value, pnl, pnl_pct])

#     df = pd.DataFrame(rows, columns=[
#         "Ticker", "Qty", "Avg", "Price", "Value", "PnL", "PnL%"
#     ])

#     st.dataframe(df, use_container_width=True)

#     st.metric("Portfolio Value", f"{total_value:.2f}")


with tab2:

    positions = build_positions()

    rows = []

    total_cost = 0
    total_value = 0

    for t, p in positions.items():

        price = get_price(t)
        if not price:
            continue

        cost = p["qty"] * p["avg"]
        value = p["qty"] * price

        pnl = value - cost
        pnl_pct = (pnl / cost) * 100 if cost else 0

        total_cost += cost
        total_value += value

        rows.append([t, p["qty"], p["avg"], price, value, pnl, pnl_pct])

    df = pd.DataFrame(rows, columns=[
        "Ticker", "Qty", "Avg", "Price", "Value", "PnL", "PnL%"
    ])

    st.dataframe(df, use_container_width=True)

    # =========================
    # 👉 PnL TOTAL
    # =========================
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0

    st.metric(
        label="Portfolio Value",
        value=f"${total_value:,.2f}",
        delta=f"${total_pnl:,.2f} ({total_pnl_pct:.2f}%)",
        delta_color="normal"  # verde si positivo, rojo si negativo
    )


# =========================
# EQUITY
# =========================
with tab3:

    df = equity_curve()

    st.area_chart(df.set_index("date"))

# =========================
# RISK
# =========================
with tab4:

    df = pd.DataFrame([
        {"Ticker": k, "Volatility": v}
        for k, v in risk_by_asset().items()
    ])

    st.dataframe(df)

# =========================
# BENCHMARK
# =========================
with tab5:

    sp = benchmark()

    st.line_chart(sp)

#   correr desde consola -->        python -m streamlit run app.py
#   correr para entrar db -->       python -m sqlite3 .\portfolio.db


