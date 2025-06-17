import streamlit as st
import json
import os
import random
from datetime import datetime
from utils import load_users, save_users, load_trades, save_trades, load_closed_trades, save_closed_trades

st.set_page_config(page_title="Moneyhub Demo", layout="wide")

st.markdown("""
    <style>
    /* GLOBAL RESET – force light background and dark text everywhere */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Fix ALL text elements (markdown, labels, sidebar, headers) */
    [data-testid="stMarkdownContainer"], .css-1v0mbdj, .css-10trblm, .css-qrbaxs, label, h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }

    /* Input fields (text, number, date, select) */
    input, textarea, select {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }

    /* Specific Streamlit component overrides */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Placeholder text */
    input::placeholder, textarea::placeholder {
        color: #666666 !important;
    }

    /* Sidebar fix */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)


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

view = st.sidebar.radio("Navigation", ["Submit Trade", "View Trades", "My Portfolio", "Leaderboard", "💡 Tips & Strategy"])

if view == "Submit Trade":
    st.header("\U0001F4DD Submit Trade Offer")
    st.markdown("""
    <div style='background-color:#eafaf1; padding:14px; border-radius:10px; font-size:15px;'>
    <b>Why place a trade?</b><br>
    Submitting a trade is your way of making a move in the market! 💥 Whether you want to <b>Buy</b> shares or <b>Sell</b> what you already own, this is how you start.
    <br><br>
    Once submitted, your offer appears in the "View Trades" tab — classmates can accept your deal and you'll see your portfolio and cash balance update automatically.
    <br><br>
    <i>Tip: Be the first to post trades to get the market moving!</i> 🕹️
    </div>
    """, unsafe_allow_html=True)

    ticker = st.text_input("Ticker (e.g. AAPL)", 
    placeholder="Type a stock symbol or anything fun!",
    help="Real tickers like AAPL, MSFT are fine — but feel free to have fun (e.g., 'Charizard', 'SodaCo')."
    )
    direction = st.selectbox("Direction", ["Buy", "Sell"])
    price = st.number_input("Price per Share", min_value=1.0, help="Choose the price you're offering for each share. Keep it realistic or get creative!")
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
    #Defining News function, to add some flare
    news_by_view = {
        "View Trades": [
            "📢 Big trades are heating up the classroom market!",
            "🔥 Trade volume hits new highs!",
        ],
        "My Portfolio": [
            "💼 Review your positions. The bell rings soon!",
            "🧠 Smart traders know when to take profit.",
        ]
    }
    news = random.choice(news_by_view.get(view, []))
    st.info(news)

    # ✨ Education Box
    st.markdown("""
    <div style='background-color:#fff3cd; padding:12px; border-radius:10px; font-size:14px; margin-bottom:15px;'>
    <b>How It Works:</b><br>
    You're looking at trade offers from classmates. If someone wants to <b>Buy</b>, you can <b>Sell</b> to them (and vice versa). 
    <br>Clicking “Accept” means you're taking the <b>other side</b> of their trade — just like how real markets work!
    </div>
    """, unsafe_allow_html=True)

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
                    📈 Wants to <b>{trade['direction']} {trade['quantity']} shares of {trade['ticker']}</b><br>
                    💵 At Price: <b>${trade['price']:.2f}</b>
                    <hr style='margin:10px 0;'>
                    You would be <b>{"selling" if trade["direction"]=="Buy" else "buying"}</b> these shares.
                </div>
                """, unsafe_allow_html=True)
            with col2:
                button_label = f"✅ {'Sell' if trade['direction']=='Buy' else 'Buy'} to {trade['user']}"
                if st.button(button_label, key=f"match_{i}"):
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

                        # Buyer's position
                        if ticker in users[buyer]["positions"]:
                            old_qty = users[buyer]["positions"][ticker]["qty"]
                            old_price = users[buyer]["positions"][ticker]["entry_price"]
                            new_qty = old_qty + qty
                            avg_price = (old_price * old_qty + price * qty) / new_qty
                            users[buyer]["positions"][ticker] = {"qty": new_qty, "entry_price": avg_price}
                        else:
                            users[buyer]["positions"][ticker] = {"qty": qty, "entry_price": price}

                        # Seller's position (short if not previously owned)
                        if ticker in users[seller]["positions"]:
                            users[seller]["positions"][ticker]["qty"] -= qty
                        else:
                            users[seller]["positions"][ticker] = {"qty": -qty, "entry_price": price}

                        trade["matched"] = True
                        save_users(USERS_FILE, users)
                        save_trades(TRADES_FILE, trades)

                        st.success(f"🎯 You just {'sold' if reverse == 'Sell' else 'bought'} {qty} shares of {ticker} at ${price:.2f}!")
                        st.balloons()
                    else:
                        st.error("You don't have enough cash to complete this trade.")



# Portfolio View --------------
elif view == "My Portfolio":
    st.header("\U0001F4C8 My Portfolio")
    st.subheader("\U0001F4B5 Account Summary")
     #Defining News function, to add some flare
    news_by_view = {
        "View Trades": [
            "📢 Big trades are heating up the classroom market!",
            "🔥 Trade volume hits new highs!",
        ],
        "My Portfolio": [
            "💼 Review your positions. The bell rings soon!",
            "🧠 Smart traders know when to take profit.",
        ]
    }
    news = random.choice(news_by_view.get(view, []))
    st.info(news)
    net_worth = user_data["cash"] + sum(
        pos["qty"] * round(pos["entry_price"] * random.uniform(0.95, 1.05), 2)
        for pos in user_data.get("positions", {}).values()
    )

    col1, col2 = st.columns(2)
    col1.metric("Cash", f"${user_data['cash']:,.2f}",help="This is how much fake money you have available to trade.")
    col2.metric("Est. Net Worth", f"${net_worth:,.2f}",help="This is your cash + the estimated value of your open positions.")
    
    #Educational Text
    st.markdown("""
    <div style='background-color:#e6f2ff; padding:14px; border-radius:10px; font-size:15px;'>
    <b>Why close a position?</b><br>
    Closing a trade means you're locking in your profit or loss. 💰 Whether you made a good call or not, this is how traders <b>realize their gains</b> and get their cash back.
    <br><br>
    Once closed, your PnL is recorded in your trade history and your net worth updates instantly. <i>Smart traders know when to take profit — or cut losses.</i> ✂️
    </div>
    """, unsafe_allow_html=True)

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
                entry_price = pos["entry_price"]
                qty = pos["qty"]
                market_price = round(entry_price * random.uniform(0.95, 1.05), 2)
                pnl = qty * (market_price - entry_price)
                direction = "Long" if qty > 0 else "Short"

                # Adjust cash correctly
                if qty > 0:
                    user_data["cash"] += qty * market_price
                else:
                    user_data["cash"] -= abs(qty) * market_price

                # Remove the position
                user_data["positions"][ticker]["qty"] = 0

                closed_trades.append({
                    "user": username,
                    "ticker": ticker,
                    "qty": qty,
                    "entry_price": entry_price,
                    "exit_price": market_price,
                    "pnl": pnl,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "direction": direction
                })

                save_users(USERS_FILE, users)
                save_closed_trades(closed_trades)

                st.success(f"Closed {direction.lower()} position in {ticker} at ${market_price:.2f}. PnL: ${pnl:+.2f}")


    st.subheader("\U0001F4DC Closed Trades History")
    my_closed_trades = [t for t in closed_trades if t["user"] == username]
    if not my_closed_trades:
        st.info("You haven't closed any trades yet.")
    else:
        st.table({
            "Ticker": [t["ticker"] for t in my_closed_trades],
            "Qty": [t["qty"] for t in my_closed_trades],
            "Side": [t.get("direction", "Long") for t in my_closed_trades],
            "Entry": [f"${t['entry_price']}" for t in my_closed_trades],
            "Exit": [f"${t['exit_price']}" for t in my_closed_trades],
            "PnL": [f"${t['pnl']:+.2f}" for t in my_closed_trades],
            "Time": [t["timestamp"] for t in my_closed_trades],
        })


# Tips and Strategy --------------
elif view == "💡 Tips & Strategy":
    st.header("💡 Trading Tips & Strategy")

    st.markdown("""
    <div style='background-color:#fdf2e9; padding:15px; border-radius:10px; font-size:15px;'>
    <b>📈 What is Trading?</b><br>
    Trading is how people buy and sell things they believe have value — like company shares, Pokémon cards, or even sneakers! When you submit a trade, you’re saying “I think this is worth X.”
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background-color:#f0f9ff; padding:15px; border-radius:10px; font-size:15px;'>
    <b>📊 Why Do Prices Move?</b><br>
    Prices go up when more people want to buy than sell. They go down when more people want to sell. That’s why your classmates’ actions matter — just like in the real stock market!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background-color:#f9f9f9; padding:15px; border-radius:10px; font-size:15px;'>
    <b>💰 When Should You Close a Trade?</b><br>
    Great question! If your trade made money (PnL is green), you might want to take profit. But sometimes it's smart to cut a loss early to protect your cash. There’s no perfect answer — only strategy.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background-color:#eafaf1; padding:15px; border-radius:10px; font-size:15px;'>
    <b>📘 What Is PnL?</b><br>
    PnL stands for "Profit and Loss." It shows how much you’ve gained or lost. You only lock in your PnL when you close the trade.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background-color:#fef9e7; padding:15px; border-radius:10px; font-size:15px;'>
    <b>🌍 Why This Matters</b><br>
    Learning to trade teaches decision-making, risk-taking, and how to think like an investor. Whether you go into business, sports, or tech — strategy and timing always matter.
    </div>
    """, unsafe_allow_html=True)


# Leaderboard --------------
elif view == "Leaderboard":
    st.header("🏆 Leaderboard")

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
        badges[leaderboard[0][0]] = "👑 Top Trader of the Day 🥇"
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
