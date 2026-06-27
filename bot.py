import discord
from discord.ext import commands
import re
from collections import defaultdict
import os

TOKEN = os.getenv("DISCORD_TOKEN")

KANAL_SADNJE = 1518237730029437241
KANAL_KOMANDE = 1517872592244052038
CENA_PO_SADNJI = 30

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot je online kao {bot.user}")

@bot.command(name="ukupnesadnje")
async def ukupne_sadnje(ctx):
    if ctx.channel.id != KANAL_KOMANDE:
        return

    kanal = bot.get_channel(KANAL_SADNJE)

    if kanal is None:
        await ctx.send("Ne mogu da pronađem kanal za sadnje.")
        return

    sadnje = defaultdict(int)

    async for msg in kanal.history(limit=None):
        text = msg.content

        user_match = re.search(r"<@!?(\d+)>", text)
        total_match = re.search(r"Ukupan broj sadnji:\s*(\d+)", text)

        if user_match and total_match:
            user_id = int(user_match.group(1))
            broj = int(total_match.group(1))
            sadnje[user_id] += broj

    if not sadnje:
        await ctx.send("Nema pronađenih sadnji.")
        return

    poruke = []

    for user_id, ukupno in sorted(sadnje.items(), key=lambda x: x[1], reverse=True):
        za_isplatu = ukupno * CENA_PO_SADNJI
        poruke.append(
            f"<@{user_id}> Ukupne sadnje: **{ukupno}**\n"
            f"Ukupno za isplatiti: **{ukupno} × {CENA_PO_SADNJI}$ = {za_isplatu}$**"
        )

    output = "\n\n".join(poruke)

    for i in range(0, len(output), 1900):
        await ctx.send(output[i:i+1900])

bot.run(TOKEN)
