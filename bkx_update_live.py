import pandas as pd
import yfinance as yf
from fredapi import Fred
import os
from datetime import datetime

# Load FRED API key
FRED_API_KEY = os.getenv("FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

# === Pull KBE Price Data (with safety check) ===
kbe_raw = yf.download("KBE", start="2000-01-01", interval="1mo", auto_adjust=True)

if 'Close' not in kbe_raw.columns:
    raise ValueError("Failed to fetch 'Close' prices for KBE — check yfinance or symbol availability.")

kbe = kbe_raw[['Close']].rename(columns={"Close": "BKX_Price"})

# === Pull Macro Data ===
cci = fred.get_series('UMCSENT').rename("CCI").resample('MS').last()
claims = fred.get_series('IC4WSA').rename("Claims").resample('MS').mean()
curve = fred.get_series('T10Y2Y').rename("Yield_Curve").resample('MS').last()

# PMI proxy
pmi_proxy = fred.get_series('CUSR0000SAD').rename("PMI").resample('MS').last()

# === Combine All Data ===
df = kbe.join([cci, pmi_proxy, claims, curve], how='inner')
print("Joined DataFrame columns:", df.columns.tolist())
print("Last available row:", df.tail(1))

# === Feature Engineering ===
df['CCI_Change_1M'] = df['CCI'].diff()
df['Claims_YoY'] = df['Claims'].pct_change(periods=12) * 100
df['BKX_1M_Return'] = df['BKX_Price'].pct_change(periods=1).shift(-1) * 100
df['BKX_3M_Return'] = df['BKX_Price'].pct_change(periods=3).shift(-3) * 100
df['BKX_6M_Return'] = df['BKX_Price'].pct_change(periods=6).shift(-6) * 100

# === Signal Scoring ===
cci_threshold = df['CCI'].quantile(0.3)

def score_row(row):
    score = 0
    if row['CCI'] < cci_threshold: score += 1
    if row['CCI_Change_1M'] > 0: score += 1
    if row['PMI'] > 50: score += 1
    if row['Yield_Curve'] > 0: score += 1
    if row['Claims_YoY'] < 0: score += 1
    return score

df['Signal_Score'] = df.apply(score_row, axis=1)

def strength(score):
    if score >= 4: return "Strong"
    elif score >= 2: return "Medium"
    return "None"

df['Signal_Strength'] = df['Signal_Score'].apply(strength)

# === Placeholder Trade Columns ===
df['Exit_Signal'] = 0
df['Entry_Date'] = ""
df['Exit_Date'] = ""
df['Entry_Price'] = ""
df['Exit_Price'] = ""
df['Trade_Return'] = ""

# === Trim to Latest Complete Month ===
last_valid_month = pd.to_datetime(datetime.today().date().replace(day=1)) - pd.offsets.MonthEnd(1)
df = df[df.index <= last_valid_month]

# === Save ===
df.index.name = 'Date'
df.to_csv("bkx_data.csv")
print("Saved: bkx_data.csv")
print("Most recent row:")
print(df.tail(1))
