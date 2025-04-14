import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('bkx_data.csv', parse_dates=['Date'])
df['Date'] = pd.to_datetime(df['Date'])

# Dashboard Title
st.title("BKX Buy Signal Dashboard (Upgraded)")
st.markdown("This model uses macroeconomic indicators and valuation filters to generate forward-looking buy signals for the BKX index.")

# Signal Overview
latest = df.iloc[-1]
st.subheader("Latest Signal Status")
if latest['Signal_Score'] >= 2:
    st.success(f"**Buy Signal: {latest['Signal_Strength']}** as of {latest['Date'].strftime('%b %Y')}")
else:
    st.info("No active buy signal this month.")

st.markdown(f"""
- **Signal Score:** {latest['Signal_Score']}
- **CCI:** {latest['CCI']} ({latest['CCI_Change_1M']} MoM)
- **PMI:** {latest['PMI']}
- **Jobless Claims YoY Change:** {latest['Claims_YoY']}%
- **BKX P/E:** {latest['BKX_PE']} | **P/B:** {latest['BKX_PB']}
- **Yield Curve (10Y-2Y):** {latest['Yield_Curve']}
""")

# Buy Signal History
st.subheader("Historical Buy Signals")
signal_df = df[df['Signal_Score'] >= 2][['Date', 'CCI', 'PMI', 'BKX_PE', 'BKX_3M_Return', 'Signal_Strength']]
st.dataframe(signal_df)

# Line chart with markers
st.subheader("BKX Price with Signal Markers")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df['Date'], df['BKX_Price'], label='BKX Price', linewidth=2)
ax.scatter(df[df['Signal_Score'] >= 2]['Date'], df[df['Signal_Score'] >= 2]['BKX_Price'], color='green', label='Buy Signal', zorder=5)
ax.set_ylabel("BKX Price")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Rolling Stats
st.subheader("Signal Performance Summary")
avg_return = signal_df['BKX_3M_Return'].mean()
hit_rate = (signal_df['BKX_3M_Return'] > 0).mean() * 100
st.markdown(f"""
- **Avg 3-Month Return After Signal:** {avg_return:.1f}%
- **Hit Rate (positive return):** {hit_rate:.1f}%
- **# of Signals:** {len(signal_df)}
""")

st.caption("Signal score combines consumer confidence, macro momentum, valuation, and yield curve conditions.")