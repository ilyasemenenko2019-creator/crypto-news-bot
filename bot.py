import os
import feedparser
import telegram
import asyncio
import random
import requests

from datetime import datetime
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telegram.Bot(token=TOKEN)

translator = GoogleTranslator(
    source='auto',
    target='ru'
)

posted_news = set()

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
]

emojis = ["🚀", "🔥", "📈", "💰", "⚡", "🪙"]

hashtags = """
#crypto #bitcoin #btc #ethereum #eth #крипта
"""

def get_crypto_prices():

    try:

        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

        data = requests.get(url).json()

        btc = data["bitcoin"]["usd"]
        eth = data["ethereum"]["usd"]

        return btc, eth

    except:

        return "N/A", "N/A"

def get_fear_greed():

    try:

        data = requests.get(
            "https://api.alternative.me/fng/"
        ).json()

        return data["data"][0]["value"]

    except:

        return "N/A"

async def send_news():

    btc_price, eth_price = get_crypto_prices()

    fear = get_fear_greed()

    for rss in RSS_FEEDS:

        feed = feedparser.parse(rss)

        for entry in feed.entries[:3]:

            if entry.link not in posted_news:

                try:

                    title_ru = translator.translate(
                        entry.title
                    )

                    emoji = random.choice(emojis)

                    current_time = datetime.now().strftime("%H:%M")

                    message = f"""
{emoji} <b>КРИПТО НОВОСТИ</b>

📰 <b>{title_ru}</b>

💵 BTC: ${btc_price}
💎 ETH: ${eth_price}

😱 Fear & Greed: {fear}

🕒 {current_time}

🔗 <a href="{entry.link}">Источник</a>

{hashtags}
"""

                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=message,
                        parse_mode="HTML",
                        disable_web_page_preview=False
                    )

                    posted_news.add(entry.link)

                    print("Отправлено:", title_ru)

                except Exception as e:

                    print("Ошибка:", e)

async def main():

    while True:

        await send_news()

        print("Ждем 5 минут...")

        await asyncio.sleep(300)

asyncio.run(main())