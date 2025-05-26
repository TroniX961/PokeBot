import discord
from discord.ext import commands, tasks
import os
import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1376580028636205238  # ❗ Ersetze das mit der Channel-ID deines Angebotskanals

@bot.event
async def on_ready():
    print(f"Bot ist eingeloggt als {bot.user}")
    daily_post.start()

@tasks.loop(hours=24)
async def daily_post():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        now = datetime.datetime.now().strftime("%d.%m.%Y")
        await channel.send(f"🛒 **Tägliche Pokémon-Angebote ({now})**\n*Hier erscheinen bald die neuesten Angebote!*")

bot.run(os.getenv("DISCORD_TOKEN"))
