import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD
from ta.volatility import BollingerBands

BASE_URL = "https://api.binance.com/api/v3/klines"

def get_ohlcv(symbol="BTCUSDT", interval="1h", limit=100):
    """Fetch OHLCV from Binance public API"""
    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    data = r.json()
    cols = ['timestamp','open','high','low','close','volume','_', '__','___','____','_____','______']
    return pd.DataFrame(data, columns=cols)

def get_indicators(symbol="BTCUSDT", interval="1h"):
    """Return (price, indicators dict)"""
    df = get_ohlcv(symbol, interval)
    df['close'] = df['close'].astype(float)
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    df['ma50'] = SMAIndicator(df['close'], window=50).sma_indicator()
    df['ma200'] = SMAIndicator(df['close'], window=200).sma_indicator()
    bb = BollingerBands(df['close'], window=20, window_dev=2)
    df['bbw'] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()
    macd = MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['macd'] = macd.macd()
    df['macdsignal'] = macd.macd_signal()
    latest = df.iloc[-1]
    price = float(latest['close'])
    return price, {
        "rsi": latest['rsi'],
        "ma50": latest['ma50'],
        "ma200": latest['ma200'],
        "bbw": latest['bbw'],
        "macd": latest['macd'],
        "macdsignal": latest['macdsignal']
    }
