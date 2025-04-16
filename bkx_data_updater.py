import pandas as pd
import yfinance as yf
from fredapi import Fred

# === YOUR FRED API KEY HERE ===
FRED_API_KEY = 'YOUR_FRED_API_KEY'
fred = Fred(api_key=FRED_API_KEY)

# === Date Range ===
start_date = "2000-01-01"

# === Pull KBE Monthly Prices ===
kbe = yf.download("KBE", start=start_date, interval="1mo")['Adj Close'].rename("KBE_Price").to_frame()

# === Pull Macro Data from FRED ===
cci = fred.get_series('CONCCON').rename("CCI").resample('M').last()
pmi = fred.get_series('NAPM').rename("PMI").resample('M').last()
claims = fred.get_series('IC4WSA').rename("Claims").resample('M').mean()
curve = fred.get_series('T10Y2Y').rename("Yield_Curve").resample('M').last()

# === Combine Into DataFrame ===
df = kbe.join([cci, pmi, claims, curve], how='inner')

# === Feature Engineering ===
df['CCI_Change_1M'] = df['CCI'].diff()
df['BKX_1M_Forward'] = df['KBE_Price'].shift(-1)
df['BKX_3M_Forward'] = df['KBE_Price'].shift(-3)
df['BKX_6M_Forward'] = df['KBE_Price'].shift(-6)

df['BKX_1M_Return'] = ((df['BKX_1M_Forward'] - df['KBE_Price']) / df['KBE_Price']) * 100
df['BKX_3M_Return'] = ((df['BKX_3M_Forward'] - df['KBE_Price']) / df['KBE_Price']) * 100
df['BKX_6M_Return'] = ((df['BKX_6M_Forward'] - df['KBE_Price']) / df['KBE_Price']) * 100

# === Clean and Save ===
df = df.drop(columns=['BKX_1M_Forward', 'BKX_3M_Forward', 'BKX_6M_Forward'])
df = df.dropna()
df.index.name = 'Date'
df.to_csv("bkx_auto_data.csv")

print("Saved: bkx_auto_data.csv")