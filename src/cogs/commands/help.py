import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import create_actionrow
from handlers.setup import GUILD_IDS, EMBED_COLOR, invite_url
from handlers.discord_utils import button


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help = {
            "ping": "`/ping`: 🏓 Pong! Measure the bot's latency.",
            "board": "`/board`: Show the current canvas' state.",
            "detemplatize": (
                "`/detemplatize <url>`: Get the original image from a pxls.space"
                " template link."
            ),
            "cooldown": "`/cooldown`: Get the current cooldown.",
            "layer": (
                "`/layer <template_0> <template_1> {template_2} ...` : Layers multiple"
                " templates on top of each other, prioritized by order. You can use"
                " template links or names from the tracker."
            ),
            "reduce": (
                "`/reduce <url>`: Convert any image to the pxls palette. url should be"
                " a link to an image."
            ),
            "users": "`/users`: Show the number of active users on pxls.space.",
            "progress": (
                "`/progress <template>`: See how much of a template has been placed!"
                " You can use template links or names from the tracker."
            ),
            "template add": (
                "`/template add <name> <url>`: Add a template to the"
                " tracker under a chosen name."
            ),
            "template remove": (
                "`/template remove <name>`: Remove one of your templates from the"
                " tracker."
            ),
            "template list": (
                "`/template list {percentage up|percentage down|pixels left}`:"
                "Show all templates in the global tracker! "
            ),
            "template show": (
                "`/template view <name>`: Display a preview of a template from the"
                " tracker."
            ),
            "template update": (
                "`/template update <name> <url>`: Change the link for a template"
                " already in the tracker."
            ),
        }

    @cog_ext.cog_slash(
        name="help", description="List all commands", guild_ids=GUILD_IDS
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _help(self, ctx: SlashContext):
        embed = discord.Embed(
            title="Command help",
            description="\n".join("• " + desc for desc in self.help.values()),
            color=EMBED_COLOR,
        )
        embed.set_footer(
            text="<param> is a mandatory parameter. {param} is an optional parameter."
        )
        invite_button = button("Invite link", style="URL", url=invite_url)
        await ctx.send(embed=embed, components=[create_actionrow(invite_button)])


def setup(bot):
    bot.add_cog(HelpCommand(bot))
