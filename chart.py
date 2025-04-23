import requests

def fetch_tradingview_snapshot(symbol, timeframe="1h"):
    """Return URL of chart snapshot from TradingView (public snapshot API)"""
    # Example using TradingView's image chart widget
    return f"https://api.tradingview.com/chart/snapshot?symbol={symbol}&interval={timeframe}"
