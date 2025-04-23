def analyze_dca(ind, price):
    """Return (signal, reason) based on indicators"""
    rsi = ind['rsi']
    ma50 = ind['ma50']
    ma200 = ind['ma200']
    bbw = ind['bbw']
    macd = ind['macd']
    macdsignal = ind['macdsignal']
    if rsi > 70:
        return "Giảm hoặc tạm ngừng DCA", "RSI cao → quá mua."
    if rsi < 30:
        return "Tăng mạnh DCA", "RSI thấp → quá bán."
    if price > ma200:
        if bbw > 0.15:
            return "DCA đều đặn", "Giá trên MA200 & BBW cao."
        return "DCA nhẹ", "Giá trên MA200 & BBW thấp."
    if price < ma200:
        return "Tăng dần DCA", "Giá dưới MA200."
    return "Giữ nguyên DCA", "Không có tín hiệu rõ ràng."
