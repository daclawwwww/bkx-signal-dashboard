import pandas as pd
import yfinance as yf
from fredapi import Fred
import os

# === Get FRED API Key from GitHub Secrets or local env ===
FRED_API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=FRED_API_KEY)

# === Pull KBE price data (BKX proxy) ===
kbe = yf.download("KBE", start="2000-01-01", interval="1mo")['Adj Close'].rename("KBE_Price").to_frame()

# === Pull FRED macro data ===
cci = fred.get_series('CONCCON').rename("CCI").resample('M').last()
pmi = fred.get_series('NAPM').rename("PMI").resample('M').last()
claims = fred.get_series('IC4WSA').rename("Claims").resample('M').mean()
curve = fred.get_series('T10Y2Y').rename("Yield_Curve").resample('M').last()

# === Combine everything into one DataFrame ===
df = kbe.join([cci, pmi, claims, curve], how='inner')

# === Feature engineering ===
df['CCI_Change_1M'] = df['CCI'].diff()

# Forward returns
df['BKX_1M_Forward'] = df['KBE_Price'].shift(-1)
df['BKX_3M_Forward'] = df['KBE_Price'].shift(-3)
df['BKX_6M_Forward'] = df['KBE_Price'].shift(-6)

df['BKX_1M_Return'] = ((df['BKX_1M_Forward'] - df['KBE_Price']) / df['KBE_Price']) * 100
df['BKX_3M_Return'] = ((df['BKX_3M_Forward'] - df['KBE_Price']) / df['KBE_Price']) * 100
df['BKX_6M_Return'] = ((df['BKX_6M_Forward'] - df['KBE_Price']) / df['KBE_Price']) * 100

# Drop temp columns and NaNs
df.drop(columns=['BKX_1M_Forward', 'BKX_3M_Forward', 'BKX_6M_Forward'], inplace=True)
df.dropna(inplace=True)

# === Save to bkx_data.csv (overwrites old) ===
df.index.name = 'Date'
df.to_csv("bkx_data.csv")

print("Saved: bkx_data.csv")