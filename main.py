import discord
from discord.ext import commands, tasks
import os
import json
import datetime
from dotenv import load_dotenv
from indicators import get_indicators
from dca_logic import analyze_dca

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # your Discord Bot Token
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # target channel ID
STATUS_FILE = "dca_status.json"
HISTORY_FILE = "dca_history.json"

# Validate environment
if not TOKEN or not CHANNEL_ID:
    raise RuntimeError("Missing DISCORD_TOKEN or DISCORD_CHANNEL_ID in environment")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

last_signal = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    dca_auto_check.start()

@bot.command(name="check")
async def check_dca(ctx, symbol: str = "BTCUSDT", timeframe: str = "1h"):
    """
    Manual check: !check SYMBOL TIMEFRAME
    """
    try:
        price, indicators = get_indicators(symbol.upper(), timeframe)
        signal, reason = analyze_dca(indicators, price)
        response = (
            f"\U0001F4CA Tín hiệu DCA cho *{symbol.upper()}* [{timeframe}]:\n"
            f"- Giá: ${price:,.2f}\n"
            f"- RSI: {indicators['rsi']:.2f}\n"
            f"- MA50: {indicators['ma50']:.2f}\n"
            f"- MA200: {indicators['ma200']:.2f}\n"
            f"- BBW: {indicators['bbw']:.4f}\n"
            f"- MACD: {indicators['macd']:.2f}\n"
            f"- MACD Signal: {indicators['macdsignal']:.2f}\n\n"
            f"\u2728 **Gợi ý DCA:** {signal}\n"
            f"🔍 *{reason}*"
        )
        await ctx.send(response)
        save_to_history(symbol.upper(), timeframe, price, indicators, signal, reason)
    except Exception as e:
        await ctx.send(f"\u274C Lỗi: {e}")

@bot.command(name="history")
async def show_history(ctx):
    """
    Show last 5 recorded signals: !history
    """
    if not os.path.exists(HISTORY_FILE):
        return await ctx.send("\u2753 Không có lịch sử nào được lưu.")
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    if not history:
        return await ctx.send("\u2753 Không có lịch sử nào được lưu.")
    latest = history[-5:]
    msg = "\U0001F4D3 *5 tín hiệu DCA gần nhất:*\n"
    for e in latest:
        ts = e['timestamp'][:19].replace("T", " ")
        msg += f"\n• {ts} - {e['symbol']} [{e['timeframe']}] → *{e['signal']}*"
    await ctx.send(msg, allowed_mentions=discord.AllowedMentions.none())

@tasks.loop(minutes=15)
async def dca_auto_check():
    """Automatic check every 15 minutes"""
    channel = bot.get_channel(int(CHANNEL_ID))
    symbol = "BTCUSDT"
    timeframe = "1h"
    try:
        price, indicators = get_indicators(symbol, timeframe)
        signal, reason = analyze_dca(indicators, price)
        global last_signal
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                last_signal = json.load(f)
        prev = last_signal.get(symbol)
        if signal != prev:
            await channel.send(
                f"\u26A1 Tín hiệu DCA thay đổi cho {symbol}: **{signal}**\n"
                f"🔍 {reason}"
            )
            last_signal[symbol] = signal
            with open(STATUS_FILE, "w") as f:
                json.dump(last_signal, f)
            save_to_history(symbol, timeframe, price, indicators, signal, reason)
    except Exception as e:
        print(f"[Auto Check Error] {e}")


def save_to_history(symbol, timeframe, price, indicators, signal, reason):
    """Append entry to HISTORY_FILE"""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "price": price,
        "indicators": indicators,
        "signal": signal,
        "reason": reason
    }
    hist = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            hist = json.load(f)
    hist.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist, f, indent=2)

bot.run(TOKEN)
