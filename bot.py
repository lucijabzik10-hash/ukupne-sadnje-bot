import discord
from discord.ext import commands
import os
import re
from collections import defaultdict

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN nije podešen.")

KANAL_SADNJE = 1518237730029437241
KANAL_ISPLATA = 1517872592244052038
CENA_PO_SADNJI = 30

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def tekst_poruke(msg):
    tekst = msg.content or ""

    for e in msg.embeds:
        data = e.to_dict()
        tekst += "\n" + str(data)

    return tekst

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("Bot radi ✅")

@bot.command(name="ukupnesadnje")
async def ukupnesadnje(ctx):
    if ctx.channel.id != KANAL_ISPLATA:
        return

    kanal = bot.get_channel(KANAL_SADNJE)
    if kanal is None:
        kanal = await bot.fetch_channel(KANAL_SADNJE)

    rezultati = {}

    async for msg in kanal.history(limit=2000):
        tekst = tekst_poruke(msg)

        if "Ukupan broj sadnji" not in tekst:
            continue

        total = re.search(r"Ukupan broj sadnji\D+(\d+)", tekst, re.I)
        if not total:
            continue

        ukupno = int(total.group(1))

        mention = re.search(r"<@!?(\d+)>", tekst)
        if mention:
            ime = f"<@{mention.group(1)}>"
        else:
            name = re.search(r"@([A-Za-z0-9_.\-]+)", tekst)
            ime = f"@{name.group(1)}" if name else "Nepoznat"

        if ime not in rezultati or ukupno > rezultati[ime]:
            rezultati[ime] = ukupno

    if not rezultati:
        await ctx.send("Nema pronađenih sadnji.")
        return

    linije = []
    for ime, ukupno in sorted(rezultati.items(), key=lambda x: x[1], reverse=True):
        linije.append(f"{ime} {ukupno * CENA_PO_SADNJI}$ {ukupno} sadnji")

    poruka = "\n".join(linije)

    for i in range(0, len(poruka), 1900):
        await ctx.send(poruka[i:i+1900])

bot.run(TOKEN)
