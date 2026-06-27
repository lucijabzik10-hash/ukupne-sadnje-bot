import discord
from discord.ext import commands
import os, re, json

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN nije podešen.")

KANAL_SADNJE = 1518237730029437241
KANAL_ISPLATA = 1517872592244052038
CENA_PO_SADNJI = 30
DATA_FILE = "sadnje_data.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def ucitaj_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def sacuvaj_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def tekst_poruke(msg):
    tekst = msg.content or ""
    for e in msg.embeds:
        tekst += "\n" + str(e.to_dict())
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

    trenutne_sadnje = {}

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
            user_key = mention.group(1)
            prikaz = f"<@{user_key}>"
        else:
            name = re.search(r"@([A-Za-z0-9_.\-]+)", tekst)
            if not name:
                continue
            user_key = name.group(1)
            prikaz = f"@{user_key}"

        if user_key not in trenutne_sadnje or ukupno > trenutne_sadnje[user_key]["ukupno"]:
            trenutne_sadnje[user_key] = {
                "prikaz": prikaz,
                "ukupno": ukupno
            }

    if not trenutne_sadnje:
        await ctx.send("Nema pronađenih sadnji.")
        return

    prosle_sadnje = ucitaj_data()
    linije = []

    for user_key, info in sorted(trenutne_sadnje.items(), key=lambda x: x[1]["ukupno"], reverse=True):
        trenutno = info["ukupno"]
        proslo = prosle_sadnje.get(user_key, 0)
        razlika = trenutno - proslo

        if razlika <= 0:
            continue

        isplata = razlika * CENA_PO_SADNJI

        linije.append(
            f"{info['prikaz']} {isplata}$ {razlika} sadnji"
        )

    nova_data = {
        user_key: info["ukupno"]
        for user_key, info in trenutne_sadnje.items()
    }

    sacuvaj_data(nova_data)

    if not linije:
        await ctx.send("Nema novih sadnji za isplatu.")
        return

    poruka = "\n".join(linije)

    for i in range(0, len(poruka), 1900):
        await ctx.send(poruka[i:i+1900])

bot.run(TOKEN)
