import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="Crypto Paper Bot", page_icon="🤖", layout="centered")

st.title("🤖 Crypto 15m Risk-Managed Bot")
st.write("Live paper-trading dashboard with a **2% Stop-Loss** & **4% Take-Profit** strategy.")

# User Inputs on the App UI
asset = st.selectbox("Choose Asset", ["BTC-USD", "ETH-USD"])
budget = st.number_input("Virtual Budget ($)", value=10.0, step=1.0)

SL_PCT = 0.02
TP_PCT = 0.04

def fetch_data(symbol):
    df = yf.download(symbol, interval="15m", period="5d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
    return df[['open', 'high', 'low', 'close']]

if st.button("🔍 Evaluate Market Now", type="primary"):
    with st.spinner(f"Analyzing live 15m candles for {asset}..."):
        try:
            df = fetch_data(asset)
            
            # Indicators
            df['EMA_Fast'] = df['close'].ewm(span=9, adjust=False).mean()
            df['EMA_Slow'] = df['close'].ewm(span=21, adjust=False).mean()
            macro_bullish = df['close'].iloc[-1] > df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            
            fast_val = df['EMA_Fast'].iloc[-1]
            slow_val = df['EMA_Slow'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            is_bullish_cross = (fast_val > slow_val) and macro_bullish
            
            # Display Results visually in the app
            st.metric(label=f"Current Price ({asset.replace('-USD', '/USDT')})", value=f"${current_price:,.2f}")
            
            col1, col2 = st.columns(2)
            col1.metric("Fast EMA (9)", f"{fast_val:,.2f}")
            col2.metric("Slow EMA (21)", f"{slow_val:,.2f}")
            
            if macro_bullish:
                st.success("Macro Trend Filter: **BULLISH 🟢**")
            else:
                st.error("Macro Trend Filter: **BEARISH 🔴**")
                
            if is_bullish_cross:
                st.balloons()
                st.success("### Signal Status: BUY READY 🚀")
                st.write(f"* **Virtual Budget:** ${budget:.2f}")
                st.write(f"* **Target TP (+4%):** ${current_price * (1 + TP_PCT):,.2f}")
                st.write(f"* **Stop Loss (-2%):** ${current_price * (1 - SL_PCT):,.2f}")
            else:
                st.warning("### Signal Status: CASH / HOLD 💤")
                st.write("Market is choppy or macro trend is down. Staying in cash.")
                
        except Exception as e:
            st.error(f"Error fetching data: {e}")
          
