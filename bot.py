import discord
from discord.ext import commands, tasks
import os
import datetime
import requests
from bs4 import BeautifulSoup
import time
import requests
from bs4 import BeautifulSoup

def check_smyths_offers():
    url = "https://www.smythstoys.com/de/de-de/toys/spielzeug/pokemon/boosters"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.smythstoys.com/"
    }
    
    time.sleep(2)  # Warte 2 Sekunden vor dem Request
    
    session = requests.Session()
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Fehler beim Abrufen der Smyths-Seite: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    offers = []

    for product in soup.select(".product-tile"):
        title_el = product.select_one(".product-title")
        price_el = product.select_one(".price-now")
        if title_el and price_el:
            title = title_el.text.strip()
            price = price_el.text.strip()
            if "booster" in title.lower():
                offers.append(f"{title} - {price}")

    if offers:
        return "🛍️ Smyths Angebote:\n" + "\n".join(offers)
    else:
        return "Keine aktuellen Smyths Booster-Angebote gefunden."


CHANNEL_ID = 1376580028636205238  # ❗ Ersetze das mit der Channel-ID deines Angebotskanals

@bot.event
async def on_ready():
    print(f"Bot ist eingeloggt als {bot.user}")
    await daily_post()  # ➕ Sofort eine Nachricht posten
    daily_post.start()  # ➕ Danach täglicher Rhythmus

@tasks.loop(hours=24)
async def daily_post():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel nicht gefunden!")
        return

    smyths_msg = check_smyths_offers()

    now = datetime.datetime.now().strftime("%d.%m.%Y")
    message = f"🛒 **Tägliche Pokémon-Angebote ({now})**\n\n{smyths_msg}"

    await channel.send(message)

bot.run(os.getenv("DISCORD_TOKEN"))

