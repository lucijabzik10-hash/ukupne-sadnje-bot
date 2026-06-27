import discord
from discord.ext import commands
import os
import re
from collections import defaultdict

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN nije podešen u Environment Variables.")

KANAL_SADNJE = 1518237730029437241
KANAL_ISPLATA = 1517872592244052038
CENA_PO_SADNJI = 30

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def izvuci_tekst_iz_poruke(msg):
    tekst = msg.content or ""

    for embed in msg.embeds:
        if embed.title:
            tekst += "\n" + embed.title

        if embed.description:
            tekst += "\n" + embed.description

        for field in embed.fields:
            tekst += f"\n{field.name}\n{field.value}"

        if embed.footer and embed.footer.text:
            tekst += "\n" + embed.footer.text

    return tekst


@bot.event
async def on_ready():
    print(f"Bot je online kao {bot.user}")


@bot.command(name="test")
async def test(ctx):
    await ctx.send("Bot radi ✅")


@bot.command(name="ukupnesadnje")
async def ukupnesadnje(ctx):
    if ctx.channel.id != KANAL_ISPLATA:
        await ctx.send("Ova komanda ne radi u ovom kanalu.")
        return

    kanal = bot.get_channel(KANAL_SADNJE)

    if kanal is None:
        await ctx.send("Ne mogu da pronađem kanal za sadnje.")
        return

    sadnje = defaultdict(int)

    async for msg in kanal.history(limit=1000):
        tekst = izvuci_tekst_iz_poruke(msg)

        user_match = re.search(r"<@!?(\d+)>", tekst)
        total_match = re.search(r"Ukupan broj sadnji[:\s]*(\d+)", tekst, re.IGNORECASE)

        if user_match and total_match:
            user_id = int(user_match.group(1))
            broj_sadnji = int(total_match.group(1))

            # Uzimamo najveći ukupan broj sadnji za usera
            if broj_sadnji > sadnje[user_id]:
                sadnje[user_id] = broj_sadnji

    if not sadnje:
        await ctx.send("Nema pronađenih sadnji.")
        return

    linije = []

    for user_id, ukupno in sorted(sadnje.items(), key=lambda x: x[1], reverse=True):
        isplata = ukupno * CENA_PO_SADNJI
        linije.append(f"<@{user_id}> {isplata}$ {ukupno} sadnji")

    poruka = "\n".join(linije)

    for i in range(0, len(poruka), 1900):
        await ctx.send(poruka[i:i + 1900])


bot.run(TOKEN)
