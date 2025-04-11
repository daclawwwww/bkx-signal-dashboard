import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('bkx_data.csv', parse_dates=['Date'])
df['Date'] = pd.to_datetime(df['Date'])

# Title
st.title("BKX Buy Signal Dashboard")
st.markdown("""
This dashboard identifies historical buy signals for the KBW Bank Index (BKX) based on shifts in consumer confidence and macro indicators.
""")

# Show signal table
st.subheader("Historical Buy Signals")
signal_df = df[df['Signal'] == 1][['Date', 'CCI', 'BKX_3M_Return', 'Signal_Strength']]
st.dataframe(signal_df)

# Line chart of BKX with signal markers
st.subheader("BKX Price and Buy Signals")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df['Date'], df['BKX_Price'], label='BKX Price', linewidth=2)
ax.scatter(df[df['Signal'] == 1]['Date'], df[df['Signal'] == 1]['BKX_Price'], color='green', label='Buy Signal', zorder=5)
ax.set_ylabel("BKX Price")
ax.set_xlabel("Date")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Current signal status
st.subheader("Current Signal Status")
latest = df.iloc[-1]
if latest['Signal'] == 1:
    st.success(f"**Buy Signal Active** as of {latest['Date'].strftime('%b %Y')}")
    st.write(f"Estimated 3M Forward Return: **{latest['BKX_3M_Return']}%**")
    st.write(f"Consumer Confidence: {latest['CCI']} | Signal Strength: {latest['Signal_Strength']}")
else:
    st.info("No Buy Signal Active This Month")

st.markdown("---")
st.caption("Model uses historical consumer confidence levels, macro trend shifts, and BKX price behavior to estimate forward returns.")
