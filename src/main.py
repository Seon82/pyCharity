import os
from discord.ext import commands
from discord_slash import SlashCommand
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


@bot.event
async def on_ready():
    print("Ready!")


bot.load_extension("commands.ping")
bot.load_extension("commands.users")
bot.load_extension("commands.cooldown")
bot.run(os.environ.get("TOKEN"))
