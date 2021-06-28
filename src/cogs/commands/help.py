import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from handlers.setup import GUILD_IDS, EMBED_COLOR


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help = {
            "ping": "`/ping`: 🏓 Pong! Measure the bot's latency.",
            "board": "`/board`: Show the current canvas' state.",
            "detemplatize": "`/detemplatize <url>`: Get the original image from a pxls.space tamplate link.",
            "cooldown": "`/cooldown`: Get the current cooldown.",
            "layer": "`/layer <template_0> <template_1> {template_2} ...` : Layers multiple templates on top of each other, prioritized by order. You can use template links or names from the tracker.",
            "detemplatize": "`/reduce <url>`: Convert any image to the pxls palette. url should be a link to an image.",
            "users": "`/users`: Show the number of active users on pxls.space.",
            "progress": "`/progress <template>`: See how much of a template has been placed! You can use template links or names from the tracker.",
            "template add": "`/template add <name> <url> {faction=False}`: Add a template to the global tracker under a chosen name! If you're a server manager, you can specify `faction:True` to highlight the template in your server and make it editable by any of your server's mods.",
            "template remove": "`/template remove <name>`: Remove one of your templates from the tracker.",
            "template list": "`/template list`: Show all templates in the global tracker! When run on a server, also highlights the server's templates to make it easy to see what they're working on.",
            "template show": "`/template view <name>`: Display a preview of a template from the tracker.",
        }

    @cog_ext.cog_slash(
        name="help", description="List all commands", guild_ids=GUILD_IDS
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _help(self, ctx: SlashContext):
        embed = discord.Embed(
            title="Command help",
            description="\n".join(desc for desc in self.help.values()),
            color=EMBED_COLOR,
        )
        embed.set_footer(
            text="<param> is a mandatory parameter. {param=default_value} is an optional parameter."
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCommand(bot))
