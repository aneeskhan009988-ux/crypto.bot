import yfinance as yf
import pandas as pd
import numpy as np
import datetime

ASSETS = ["BTC-USD", "ETH-USD"]
SL_PCT = 0.02
TP_PCT = 0.04

def run_background_check():
    print(f"--- Automated Bot Run at {datetime.datetime.now()} ---")
    
    for symbol in ASSETS:
        try:
            df = yf.download(symbol, interval="15m", period="5d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
            
            # Indicators
            df['EMA_Fast'] = df['close'].ewm(span=9, adjust=False).mean()
            df['EMA_Slow'] = df['close'].ewm(span=21, adjust=False).mean()
            macro_bullish = df['close'].iloc[-1] > df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            
            fast_val = df['EMA_Fast'].iloc[-1]
            slow_val = df['EMA_Slow'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            is_bullish_cross = (fast_val > slow_val) and macro_bullish
            
            print(f"Asset: {symbol} | Price: ${current_price:,.2f} | Macro: {'BULLISH' if macro_bullish else 'BEARISH'}")
            
            if is_bullish_cross:
                print(f"🚀 SIGNAL: BUY READY for {symbol}! TP: ${current_price * (1 + TP_PCT):,.2f} | SL: ${current_price * (1 - SL_PCT):,.2f}")
            else:
                print(f"💤 SIGNAL: HOLD / CASH for {symbol}")
                
        except Exception as e:
            print(f"Error checking {symbol}: {e}")

if __name__ == "__main__":
    run_background_check()
  
