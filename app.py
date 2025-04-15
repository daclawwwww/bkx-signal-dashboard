import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('bkx_data.csv', parse_dates=['Date'])
df['Date'] = pd.to_datetime(df['Date'])

# Title
st.title("BKX Buy & Exit Signal Dashboard")
st.markdown("An early signal system using consumer confidence, macro momentum, and valuation filters to flag BKX entries and exits.")

# Latest Signal Status
latest = df.iloc[-1]
st.subheader("Current Signal Status")
if latest['Signal_Score'] >= 2:
    st.success(f"**Buy Signal: {latest['Signal_Strength']}** — {latest['Date'].strftime('%b %Y')}")
else:
    st.info("No active buy signal this month.")

if latest['Exit_Signal'] == 1:
    st.warning(f"**Exit Signal Active** — {latest['Date'].strftime('%b %Y')}")

# Metrics Overview
st.markdown(f"""
- **Signal Score:** {latest['Signal_Score']}
- **CCI:** {latest['CCI']} (Δ {latest['CCI_Change_1M']})
- **PMI:** {latest['PMI']}
- **Claims YoY %:** {latest['Claims_YoY']}%
- **BKX P/E:** {latest['BKX_PE']} | **P/B:** {latest['BKX_PB']}
- **Yield Curve:** {latest['Yield_Curve']}
""")

# Buy/Exit Signal Chart
st.subheader("BKX Price with Entry/Exit Markers")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df['Date'], df['BKX_Price'], label='BKX Price', linewidth=2)
ax.scatter(df[df['Signal_Score'] >= 2]['Date'], df[df['Signal_Score'] >= 2]['BKX_Price'], color='green', label='Buy Signal', zorder=5)
ax.scatter(df[df['Exit_Signal'] == 1]['Date'], df[df['Exit_Signal'] == 1]['BKX_Price'], color='red', label='Exit Signal', zorder=5)
ax.set_ylabel("BKX Price")
ax.set_xlabel("Date")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Trade History
st.subheader("Completed Trades")
trade_df = df.dropna(subset=['Entry_Date', 'Exit_Date'])
st.dataframe(trade_df[['Entry_Date', 'Exit_Date', 'Entry_Price', 'Exit_Price', 'Trade_Return']])

# Trade Stats
st.subheader("Performance Summary")
if len(trade_df) > 0:
    avg_ret = trade_df['Trade_Return'].mean()
    win_rate = (trade_df['Trade_Return'] > 0).mean() * 100
    max_dd = trade_df['Trade_Return'].min()
    st.markdown(f"""
    - **Average Trade Return:** {avg_ret:.2f}%
    - **Win Rate:** {win_rate:.1f}%
    - **Max Drawdown (per trade):** {max_dd:.2f}%
    """)
else:
    st.info("No trades completed yet.")

st.caption("Signal Score >= 2 triggers an entry. Exit occurs when score drops <2 or CCI enters upper quartile and reverses.")