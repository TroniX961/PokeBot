import discord
from discord.ext import commands, tasks
import os
import datetime
import requests
from bs4 import BeautifulSoup
import time

# Intents definieren (z. B. um Nachrichten zu senden)
intents = discord.Intents.default()
intents.message_content = True  # Erforderlich, damit der Bot Nachrichten lesen/schreiben darf

# Bot-Objekt erstellen mit Prefix und Intents
PokeBot = commands.Bot(command_prefix="!", intents=intents)

# Channel-ID für die Angebotsnachrichten
CHANNEL_ID = 1376580028636205238

# Funktion: Smyths-Angebote prüfen
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

    time.sleep(2)  # Kurze Pause vor dem Abruf
    
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

# Lidl
def check_lidl_offers():
    url = "https://www.lidl.de/suche?query=pokemon"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.lidl.de",
        "Connection": "keep-alive"
    }

    #Galeria

def check_galeria_offers():
    url = "https://www.galeria.de/search?q=pokemon"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.6422.112 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com"
    }

    # ⏱️ Delay von 3 Sekunden, damit GALERIA den Bot nicht blockt
    time.sleep(3)

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        return f"❌ Fehler beim Abrufen der GALERIA-Seite: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    offers = []

    for product in soup.select("article.product-tile"):
        title_el = product.select_one(".product-title")
        price_el = product.select_one(".price")

        if title_el and price_el:
            title = title_el.get_text(strip=True)
            price = price_el.get_text(strip=True)

            # 🔎 Filter auf relevante Pokémon-Produkte
            if any(keyword in title.lower() for keyword in ["booster", "display", "pokemon", "blister", "einzelkarte"]):
                offers.append(f"{title} – {price}")

    if offers:
        return "🛍️ **GALERIA-Angebote:**\n" + "\n".join(offers)
    else:
        return "ℹ️ Keine aktuellen GALERIA-Angebote gefunden."

    session = requests.Session()
    time.sleep(2)  # Kurze Pause für Freundlichkeit

    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return "Keine aktuellen Lidl Pokémon-Angebote gefunden."
        response.raise_for_status()
    except Exception as e:
        return f"❌ Fehler beim Abrufen der Lidl-Seite: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    offers = []

    for item in soup.select(".product-grid-box"):
        title_el = item.select_one(".product-title")
        price_el = item.select_one(".m-price__price")

        if title_el and price_el:
            title = title_el.get_text(strip=True)
            price = price_el.get_text(strip=True)

            if "pokemon" in title.lower():
                offers.append(f"{title} – {price}")

    if offers:
        return "🛍️ Lidl-Angebote:\n" + "\n".join(offers)
    else:
        return "Keine aktuellen Lidl Pokémon-Angebote gefunden."


# Täglicher Task
@tasks.loop(hours=24)
async def daily_post():
    channel = PokeBot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel nicht gefunden!")
        return

    smyths_msg = check_smyths_offers()
    lidl_msg = check_lidl_offers()
    galeria_msg = check_galeria_offers()

    now = datetime.datetime.now().strftime("%d.%m.%Y")
    message = (
        f"🛒 **Tägliche Pokémon-Angebote ({now})**\n\n"
        f"{smyths_msg}\n\n"
        f"{lidl_msg}\n\n"
        f"{galeria_msg}"
    )

    await channel.send(message)


# Event: Bot startbereit
@PokeBot.event
async def on_ready():
    print(f"PokeBot ist eingeloggt als {PokeBot.user}")
    await daily_post()       # Sofort beim Start einmal posten
    daily_post.start()       # Danach täglich wiederholen

# Bot starten
PokeBot.run(os.getenv("DISCORD_TOKEN"))
