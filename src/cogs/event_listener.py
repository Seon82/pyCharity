import logging
from os.path import join, dirname
import discord
from discord.ext import commands
from handlers.discord_utils import UserError
from handlers.setup import EMBED_COLOR

logger = logging.getLogger("pyCharity." + __name__)


class Events(commands.Cog):
    """
    A cog used a an event listener.
    """

    def __init__(self, bot):
        self.bot = bot
        assets = join(dirname(__file__), "../assets")
        with open(join(assets, "welcome_message.txt")) as msg:
            self.welcome_message = msg.read()
        with open(join(assets, "profile.png"), "rb") as avatar:
            self.avatar = avatar.read()

    @commands.Cog.listener()
    async def on_ready(self):
        """Set activity and avatar once the bot has started up."""
        await self.bot.change_presence(
            activity=discord.Activity(
                name="pxls.space", type=discord.ActivityType.watching
            )
        )
        await self.bot.user.edit(avatar=self.avatar)
        logger.info("Ready!")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Send a presentation message."""
        logger.info(f"Joined new guild: {guild.name}")
        channels = guild.text_channels
        filtered_channels = [
            c for c in channels if c.permissions_for(c.guild.me).send_messages
        ]
        channel_ranking = {"general": 5, "bots": 4, "spam": 3}
        filtered_channels.sort(
            key=lambda c: channel_ranking.get(c.name, 0), reverse=True
        )
        if len(filtered_channels) > 0:
            embed = discord.Embed(
                title="A wild bot appeared",
                description=self.welcome_message.format(self.bot.user.name),
                color=EMBED_COLOR,
            )
            await filtered_channels[0].send(embed=embed)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        """Error message handler."""
        unexpected = False
        title = "❌ Error"
        if isinstance(error, UserError):
            description = error.args[0]
        elif isinstance(error, commands.errors.CommandOnCooldown):
            description = (
                "This command is on cooldown.",
                f"Please try again in `{error.retry_after:.2f}s`.",
            )
        else:
            unexpected = True
            description = (
                "An unexpected error occured. Please contact the bot developer."
            )
        embed = discord.Embed(title=title, description=description, color=0xCC0000)
        await ctx.send(embed=embed)
        if unexpected:
            logger.error(
                f"An error has occured while running: "
                f"/{ctx.command} {ctx.subcommand_name if ctx.subcommand_name else ''}"
            )
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
