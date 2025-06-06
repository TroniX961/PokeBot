import discord
from discord.ext import commands, tasks
import os
import datetime
import time
import requests
from bs4 import BeautifulSoup


# Intents definieren
intents = discord.Intents.default()
intents.message_content = True

# Bot initialisieren
PokeBot = commands.Bot(command_prefix="!", intents=intents)

# Channel-ID für Angebote
CHANNEL_ID = 1376580028636205238

# Smyths-Angebote
def check_smyths_offers():
    url = "https://www.smythstoys.com/de/de-de/search/?text=pokemon"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.smythstoys.com/"
    }

    time.sleep(2)

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"❌ Fehler beim Abrufen der Smyths-Seite: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    offers = []

    for product in soup.select(".product-tile"):
        title_el = product.select_one(".product-title")
        price_now = product.select_one(".price-now")
        price_was = product.select_one(".price-was")
        price_save = product.select_one(".price-save")

        if title_el and price_now and (price_was or price_save):
            title = title_el.text.strip()
            now_price = price_now.text.strip()

            if price_was:
                old_price = price_was.text.strip()
                offers.append(f"{title} – ~~{old_price}~~ → **{now_price}**")
            elif price_save:
                save_info = price_save.text.strip()
                offers.append(f"{title} – **{now_price}** ({save_info})")

    if offers:
        return "🛍️ Smyths Angebote:\n" + "\n".join(offers)
    else:
        return "Keine reduzierten Smyths Pokémon-Angebote gefunden."

# Lidl-Angebote
def check_lidl_offers():
    url = "https://www.lidl.de/de/search?query=pokemon"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, wie Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }

    time.sleep(2)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"❌ Fehler beim Abrufen der Lidl-Seite: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    offers = []

    for item in soup.select(".product-grid-box"):
        title_el = item.select_one(".product-title")
        price_now = item.select_one(".m-price__price")
        price_was = item.select_one(".m-price__strike")

        if title_el and price_now and price_was:
            title = title_el.get_text(strip=True)
            price_now = price_now.get_text(strip=True)
            price_was = price_was.get_text(strip=True)

            if "pokemon" in title.lower():
                offers.append(f"{title} – **{price_now}** statt ~~{price_was}~~")

    if offers:
        return "🏍️ Lidl-Angebote:\n" + "\n".join(offers)
    else:
        return "Keine aktuellen Lidl-Angebote gefunden."

# Galeria-Angebote mit Seleniu

# Gemeinsame Post-Funktion
async def post_daily():
    channel = PokeBot.get_channel(CHANNEL_ID)
    if channel is None:
        try:
            channel = await PokeBot.fetch_channel(CHANNEL_ID)
        except Exception as e:
            print(f"❌ Fehler beim Abrufen des Channels: {e}")
            return

    smyths_msg = check_smyths_offers()
    lidl_msg = check_lidl_offers()

    now = datetime.datetime.now().strftime("%d.%m.%Y")
    message = (
        f"🛒 **Tägliche Pokémon-Angebote ({now})**\n\n"
        f"{smyths_msg}\n\n"
        f"{lidl_msg}\n\n"
    )

    await channel.send(message)

# Wiederkehrender Task
@tasks.loop(hours=24)
async def daily_post():
    await post_daily()

# Event bei Start
@PokeBot.event
async def on_ready():
    print(f"PokeBot ist eingeloggt als {PokeBot.user}")
    await post_daily()
    if not daily_post.is_running():
        daily_post.start()

# Bot starten
PokeBot.run(os.getenv("DISCORD_TOKEN"))
