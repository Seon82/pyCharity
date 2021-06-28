import os
from discord.ext import commands
from discord_slash import SlashCommand

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


# Load commands
command_dir = os.listdir(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs/commands")
)
for file in command_dir:
    if file.endswith(".py") and file != "__init__.py":
        extension_name = file.replace(".py", "")
        bot.load_extension(f"cogs.commands.{extension_name}")
        print(f"Loaded {extension_name} command.")

# Load other cogs
for cog in ["clock", "event_listener"]:
    bot.load_extension(f"cogs.{cog}")
    print(f"Loaded {cog}.")

bot.run(os.environ.get("TOKEN"))
