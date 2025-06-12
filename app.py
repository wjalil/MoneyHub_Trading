import streamlit as st
import json
import os
import random
from datetime import datetime
from utils import load_users, save_users, load_trades, save_trades, load_closed_trades, save_closed_trades

st.set_page_config(page_title="Moneyhub Demo", layout="wide")

USERS_FILE = "data/users.json"
TRADES_FILE = "data/trades.json"
CLOSED_TRADES_FILE = "data/closed_trades.json"

users = load_users(USERS_FILE)
trades = load_trades(TRADES_FILE)
closed_trades = load_closed_trades(CLOSED_TRADES_FILE)

st.title("\U0001F4CA MoneyHub Trading Demo – Classroom Edition")

st.markdown("""
<div style='background-color:#fef9e7;padding:15px;border-radius:10px;margin-top:10px;'>
  📘 <b>Welcome to the TRS Classroom Simulator!</b><br><br>
  This app lets you simulate trading stocks with your classmates using pretend money. It's designed to help you:
  <ul>
    <li>📈 Understand how buying and selling stocks works</li>
    <li>💰 Learn how to track profit and loss (PnL)</li>
    <li>🎯 Compete to see who grows their portfolio the most</li>
  </ul>
  💡 <i>Tip: Check your leaderboard rank daily and try to reach the top!</i>
</div>
""", unsafe_allow_html=True)

username = st.text_input("Enter your name to begin:", max_chars=30)
if not username:
    st.stop()

if username not in users:
    users[username] = {"cash": 10000, "positions": {}, "pnl": 0}
    save_users(USERS_FILE, users)

user_data = users[username]
st.success(f"Welcome, {username}! Your starting cash: ${user_data['cash']:,.2f}")

view = st.sidebar.radio("Navigation", ["Submit Trade", "View Trades", "My Portfolio", "Leaderboard"])

if view == "Submit Trade":
    st.header("\U0001F4DD Submit Trade Offer")

    ticker = st.text_input("Ticker (e.g. AAPL)")
    direction = st.selectbox("Direction", ["Buy", "Sell"])
    price = st.number_input("Price per Share", min_value=1.0)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Submit Offer"):
        trade = {
            "user": username,
            "ticker": ticker.upper(),
            "direction": direction,
            "price": price,
            "quantity": quantity,
            "matched": False
        }
        trades.append(trade)
        save_trades(TRADES_FILE, trades)
        st.success("Trade submitted!")


# View Trades --------------
elif view == "View Trades":
    st.header("\U0001F4EC Open Trade Offers")
    open_trades = [t for t in trades if not t["matched"] and t["user"] != username]

    if not open_trades:
        st.info("No open trades to match right now.")
    else:
        for i, trade in enumerate(open_trades):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style='background-color:#e0f7fa;padding:15px;border-radius:12px;box-shadow:2px 2px 5px rgba(0,0,0,0.1);font-size:16px;'>
                    👤 <b>{trade['user']}</b><br>
                    📈 Wants to <b>{trade['direction']} {trade['quantity']} {trade['ticker']}</b><br>
                    💵 Price: <b>${trade['price']:.2f}</b>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button(f"🚀 Accept Trade & Join the Market!", key=f"match_{i}"):
                    reverse = "Buy" if trade["direction"] == "Sell" else "Sell"
                    total = trade["price"] * trade["quantity"]

                    buyer, seller = (
                        (username, trade["user"]) if reverse == "Buy" else (trade["user"], username)
                    )

                    if users[buyer]["cash"] >= total:
                        users[buyer]["cash"] -= total
                        users[seller]["cash"] += total

                        ticker = trade["ticker"]
                        qty = trade["quantity"]
                        price = trade["price"]

                        if ticker in users[buyer]["positions"]:
                            old_qty = users[buyer]["positions"][ticker]["qty"]
                            old_price = users[buyer]["positions"][ticker]["entry_price"]
                            new_qty = old_qty + qty
                            avg_price = (old_price * old_qty + price * qty) / new_qty
                            users[buyer]["positions"][ticker] = {"qty": new_qty, "entry_price": avg_price}
                        else:
                            users[buyer]["positions"][ticker] = {"qty": qty, "entry_price": price}

                        if ticker in users[seller]["positions"]:
                            users[seller]["positions"][ticker]["qty"] -= qty
                        else:
                            users[seller]["positions"][ticker] = {"qty": -qty, "entry_price": price}

                        trade["matched"] = True
                        save_users(USERS_FILE, users)
                        save_trades(TRADES_FILE, trades)
                        st.success(f"Trade matched successfully! 🎉 {username} just made a move in the market!")
                        st.balloons()
                    else:
                        st.error("Insufficient funds to match this trade.")


# Portfolio View --------------
elif view == "My Portfolio":
    st.header("\U0001F4C8 My Portfolio")
    st.subheader("\U0001F4B5 Account Summary")

    net_worth = user_data["cash"] + sum(
        pos["qty"] * round(pos["entry_price"] * random.uniform(0.95, 1.05), 2)
        for pos in user_data.get("positions", {}).values()
    )

    col1, col2 = st.columns(2)
    col1.metric("Cash", f"${user_data['cash']:,.2f}",help="This is how much fake money you have available to trade.")
    col2.metric("Est. Net Worth", f"${net_worth:,.2f}",help="This is your cash + the estimated value of your open positions.")

    st.subheader("\U0001F4E6 Open Positions with Estimated PnL")
    positions = user_data.get("positions", {})
    if not positions or all(pos["qty"] == 0 for pos in positions.values()):
        st.info("You don't have any active positions.")
    else:
        cols = st.columns([2, 2, 2, 2, 2])
        cols[0].markdown("**Ticker**")
        cols[1].markdown("**Quantity**")
        cols[2].markdown("**Market Price**")
        cols[3].markdown("**PnL ($)**")
        cols[4].markdown("**Action**")

        for ticker, pos in positions.items():
            qty = pos["qty"]
            if qty == 0:
                continue
            entry_price = pos["entry_price"]
            market_price = round(entry_price * random.uniform(0.95, 1.05), 2)
            pnl = qty * (market_price - entry_price)

            cols[0].write(ticker)
            cols[1].write(qty)
            cols[2].write(f"${market_price}")
            cols[3].markdown(f"<span style='color: {'green' if pnl >= 0 else 'red'};'>${pnl:+,.2f}</span>", unsafe_allow_html=True)

            if cols[4].button(f"Close {ticker}", key=f"close_{ticker}"):
                user_data["cash"] += qty * market_price  # Add full market value instead of just PnL
                user_data["positions"][ticker]["qty"] = 0
                closed_trades.append({
                    "user": username,
                    "ticker": ticker,
                    "qty": qty,
                    "entry_price": entry_price,
                    "exit_price": market_price,
                    "pnl": pnl,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_users(USERS_FILE, users)
                save_closed_trades(closed_trades)
                st.success(f"Closed position in {ticker} at ${market_price}. PnL: ${pnl:+,.2f}")

    st.subheader("\U0001F4DC Closed Trades History")
    my_closed_trades = [t for t in closed_trades if t["user"] == username]
    if not my_closed_trades:
        st.info("You haven't closed any trades yet.")
    else:
        st.table({
            "Ticker": [t["ticker"] for t in my_closed_trades],
            "Qty": [t["qty"] for t in my_closed_trades],
            "Entry": [f"${t['entry_price']}" for t in my_closed_trades],
            "Exit": [f"${t['exit_price']}" for t in my_closed_trades],
            "PnL": [f"${t['pnl']:+.2f}" for t in my_closed_trades],
            "Time": [t["timestamp"] for t in my_closed_trades],
        })

# FAQ --------------
elif view == "FAQ":
    st.header("❓ FAQ – Learn the Basics")
    st.markdown("""
    <div style='background-color:#f0f3f5;padding:15px;border-radius:10px;'>
    <ul>
      <li><b>💰 Cash:</b> This is your starting balance to trade with.</li>
      <li><b>📈 Buy/Sell:</b> Buying means you think the price will go up. Selling means you think it will go down.</li>
      <li><b>📊 PnL:</b> Stands for 'Profit and Loss'. It tells you how much you’ve gained or lost on a trade.</li>
      <li><b>💼 Net Worth:</b> Your cash + value of all open positions.</li>
      <li><b>🔁 Match Trade:</b> Accept someone else’s offer to complete a trade.</li>
    </ul>
    <i>Learning how to trade is a skill — ask questions and have fun exploring!</i>
    </div>
    """, unsafe_allow_html=True)

# Leaderboard --------------
elif view == "Leaderboard":
    st.header("🏆 Leaderboard")
    # 🎖️ Badge Assignment
   
    random.seed(42)
    all_tickers = set()
    for u in users.values():
        all_tickers.update(u.get("positions", {}).keys())
    prices = {t: round(pos["entry_price"] * random.uniform(0.95, 1.05), 2) for u in users.values() for t, pos in u.get("positions", {}).items()}

    leaderboard = []
    for name, data in users.items():
        equity = data["cash"]
        for ticker, pos in data.get("positions", {}).items():
            equity += pos["qty"] * prices.get(ticker, 100)
        leaderboard.append((name, equity))

    leaderboard.sort(key=lambda x: x[1], reverse=True)
    
    badges = {}
    if leaderboard:
        badges[leaderboard[0][0]] = "🥇"
        if len(leaderboard) > 1:
            badges[leaderboard[1][0]] = "🥈"
        if len(leaderboard) > 2:
            badges[leaderboard[2][0]] = "🥉"
    
    st.subheader("\U0001F4CA Total Net Worth (Cash + Unrealized PnL)")
    st.table({
        "Name": [f"{badges.get(x[0], '')} {x[0]}" for x in leaderboard],
        "Net Worth ($)": [f"${x[1]:,.2f}" for x in leaderboard]
    })

if username.lower() == "teacher":
    if st.sidebar.button("\U0001F9F9 Reset All Data"):
        users = {}
        trades = []
        closed_trades = []
        save_users(USERS_FILE, users)
        save_trades(TRADES_FILE, trades)
        save_closed_trades(closed_trades)
        st.warning("All user data and trades have been reset.")
