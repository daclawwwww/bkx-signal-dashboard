import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('bkx_data.csv', parse_dates=['Date'])
df['Date'] = pd.to_datetime(df['Date'])

# Use the most recent row that has signal strength data
latest = df[df['Signal_Strength'] != 'None'].iloc[-1]

# Title
st.title("BKX Buy & Exit Signal Dashboard")
st.markdown("Live macro and valuation-driven signals for bank stocks using monthly indicators and forward returns.")

# Current Signal Display
st.subheader("Current Signal Status")
if latest['Signal_Score'] >= 2:
    st.success(f"**Buy Signal: {latest['Signal_Strength']}** — {latest['Date'].strftime('%b %Y')}")
else:
    st.info("No active buy signal this month.")

if latest['Exit_Signal'] == 1:
    st.warning(f"**Exit Signal Active** — {latest['Date'].strftime('%b %Y')}")

# Macro & Valuation Display
st.markdown(f"""
- **Signal Score:** {latest['Signal_Score']}
- **CCI:** {latest['CCI']} (Δ {latest['CCI_Change_1M']})
- **PMI:** {latest['PMI']}
- **Claims YoY %:** {latest['Claims_YoY']}%
- **BKX P/E:** {latest.get('BKX_PE', '—')} | **P/B:** {latest.get('BKX_PB', '—')}
- **Yield Curve:** {latest['Yield_Curve']}
""")

# Chart
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

# Trade History Table
st.subheader("Trade History")
df['Trade_Status'] = df.apply(lambda row: "Open" if pd.isna(row['Exit_Date']) else "Closed", axis=1)
trade_df = df[df['Entry_Date'].notna()][['Entry_Date', 'Exit_Date', 'Entry_Price', 'Exit_Price', 'Trade_Return', 'Trade_Status']]
st.dataframe(trade_df)

# Trade Summary
st.subheader("Performance Summary")
closed = trade_df[trade_df['Trade_Status'] == 'Closed']
if not closed.empty:
    avg_ret = closed['Trade_Return'].mean()
    win_rate = (closed['Trade_Return'] > 0).mean() * 100
    max_dd = closed['Trade_Return'].min()
    st.markdown(f"""
    - **Average Return:** {avg_ret:.2f}%
    - **Win Rate:** {win_rate:.1f}%
    - **Max Drawdown:** {max_dd:.2f}%
    """)
else:
    st.info("No closed trades yet.")

st.caption("Signals based on macro conditions, confidence trends, and valuation filters. Dashboard powered by GitHub & FRED.")