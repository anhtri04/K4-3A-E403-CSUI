"""Live Discord gateway (thin). All policy lives in app/opencode_bridge/course_kb."""
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

HELP = ("BuildMate commands:\n"
        "`@buildmate check-tech <proposal>` — MVP-grounded verdict\n"
        "`@buildmate explain <symbol>` — cite file:line\n"
        "`@buildmate ask-course <q>` — official announcements only, else tag TA\n"
        "`@buildmate propose-diff <task>` — branch patch, needs `!approve` (never pushes main)\n"
        "`!revise <note>` `!approve` `!discard`")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"BuildMate live as {client.user}. Policy: data-not-commands, no push to main.")


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if client.user not in msg.mentions and not msg.content.startswith("!"):
        return
    # Delegate to same handlers as app.py (import lazily to keep gateway thin)
    if "help" in msg.content.lower():
        await msg.channel.send(HELP)
        return
    await msg.channel.send("Received. Full handling in `app.py` handlers (wired next). Policy: no push to main, official-only course answers.")

if __name__ == "__main__":
    assert TOKEN, "Set DISCORD_TOKEN in .env (see .env.example)"
    client.run(TOKEN)
