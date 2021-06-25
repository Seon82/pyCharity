import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from dotenv import load_dotenv

from handlers.discord_utils import UserError

load_dotenv()


bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_slash_command_error(ctx, error):
    """Error message handler."""
    unexpected = False
    title = "❌ Error"
    if isinstance(error, UserError):
        description = error.args[0]
    else:
        unexpected = True
        description = "An unexpected error occured. Please contact the bot developer."
    embed = discord.Embed(title=title, description=description, color=0xCC0000)
    await ctx.send(embed=embed)
    if unexpected:
        raise error


# Load cogs
command_dir = os.listdir(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "commands")
)
for file in command_dir:
    if file.endswith(".py") and file != "__init__.py":
        extension_name = file.replace(".py", "")
        bot.load_extension(f"commands.{extension_name}")
        print(f"Loaded {extension_name} command.")


bot.run(os.environ.get("TOKEN"))
