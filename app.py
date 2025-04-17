import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# === Load Data ===
df = pd.read_csv("bkx_data.csv", parse_dates=["Date"], index_col="Date")

# === Signal Logic ===
buy_signals = df[df["Entry_Signal"] == 1]
sell_signals = df[df["Exit_Signal"] == 1]

# === Trade Pairing ===
trades = []
in_trade = False
entry_date = None
entry_price = None

for date, row in df.iterrows():
    if not in_trade and row["Entry_Signal"] == 1:
        in_trade = True
        entry_date = date
        entry_price = row["BKX_Price"]
    elif in_trade and row["Exit_Signal"] == 1:
        exit_date = date
        exit_price = row["BKX_Price"]
        trades.append({
            "Entry_Date": entry_date,
            "Exit_Date": exit_date,
            "Entry_Price": entry_price,
            "Exit_Price": exit_price,
            "Trade_Return": round((exit_price - entry_price) / entry_price * 100, 2)
        })
        in_trade = False

trades_df = pd.DataFrame(trades)

# === Summary Stats ===
avg_return = trades_df["Trade_Return"].mean() if not trades_df.empty else 0
win_rate = (trades_df["Trade_Return"] > 0).mean() * 100 if not trades_df.empty else 0
max_drawdown = ((df["BKX_Price"].cummax() - df["BKX_Price"]) / df["BKX_Price"].cummax()).max() * -100

# === UI ===
st.title("BKX Price with Entry/Exit Markers")
st.line_chart(df["BKX_Price"])

fig, ax = plt.subplots()
ax.plot(df.index, df["BKX_Price"], label="BKX Price")
ax.scatter(buy_signals.index, buy_signals["BKX_Price"], color="green", label="Buy Signal")
ax.scatter(sell_signals.index, sell_signals["BKX_Price"], color="red", label="Exit Signal")
ax.set_ylabel("BKX Price")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

# === Trade History Table ===
st.subheader("Trade History")
st.dataframe(trades_df)

# === Performance Summary ===
st.subheader("Performance Summary")
if not trades_df.empty:
    st.markdown(f"- **Average Return:** {avg_return:.2f}%")
    st.markdown(f"- **Win Rate:** {win_rate:.1f}%")
    st.markdown(f"- **Max Drawdown:** {max_drawdown:.2f}%")
else:
    st.info("No closed trades yet.")

st.caption("Signals based on macro conditions, confidence trends, and valuation filters. Dashboard powered by GitHub & FRED.")