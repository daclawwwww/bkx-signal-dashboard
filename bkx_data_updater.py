import pandas as pd
import yfinance as yf
from fredapi import Fred
import os
from datetime import datetime

# === FRED API Key (from GitHub Secrets or env) ===
FRED_API_KEY = os.getenv("FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

# === Pull KBE Price Data ===
kbe = yf.download("KBE", start="2000-01-01", interval="1mo")['Adj Close'].rename("BKX_Price").to_frame()

# === Pull FRED Macro Data ===
cci = fred.get_series('CONCCON').rename("CCI").resample('M').last()
pmi = fred.get_series('NAPM').rename("PMI").resample('M').last()
claims = fred.get_series('IC4WSA').rename("Claims").resample('M').mean()
curve = fred.get_series('T10Y2Y').rename("Yield_Curve").resample('M').last()

# === Combine All Data ===
df = kbe.join([cci, pmi, claims, curve], how='inner')

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

# === Placeholder Trade Fields ===
df['Exit_Signal'] = 0
df['Entry_Date'] = ""
df['Exit_Date'] = ""
df['Entry_Price'] = ""
df['Exit_Price'] = ""
df['Trade_Return'] = ""

# === Drop Future Rows (avoid NaNs from unfinished months) ===
today = datetime.today()
first_of_this_month = pd.to_datetime(today.strftime('%Y-%m-01'))
df = df[df.index < first_of_this_month]

# === Save ===
df.index.name = 'Date'
df.to_csv("bkx_data.csv")
print("Saved: bkx_data.csv")
print("Most recent row:", df.tail(1))