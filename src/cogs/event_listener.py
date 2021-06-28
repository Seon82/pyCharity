import discord
from discord.ext import commands
from handlers.discord_utils import UserError
from handlers.setup import EMBED_COLOR


class Events(commands.Cog):
    """
    A cog used a an event listener.
    """

    def __init__(self, bot):
        self.bot = bot
        self.welcome_message = (
            "Glad to meet you guys! I'm {}, "
            + "a bot made to help you manage everything pxls. :smiley:\n\n"
            + "At my core, I'm a template tracker:\n"
            + "• If you're a **regular user**, you can share a template to a global dashboard by using "
            + "`/template add <name:some name> <url:your template link>`. "
            + "That's it, anyone using Charity can now see your template! "
            + "They just have to run  `/template list` in my DMs or on any server I'm on.\n\n"
            + "• If you're a **faction admin**, you can add a 'faction template' to the "
            + "global dashboard by running `/template add <name:some name> <url:your template link> "
            + "<faction:true>` on your faction's server.\nThis 'faction template' will be editable from "
            + "your server by anyone with moderator permissions  to make it easier to roll out changes. "
            + "On top of that, it will show up in a special spot when someone runs  `/template list` "
            + "on your server to make it easier for members to quickly grab the latest project.\n\n"
            + ":mag_right: I have quite a few other quality-of-life functions, you can take a better look at them "
            + "whenever you want with `/help`."
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Send a presentation message."""
        print(f"Joined new guild: {guild.name}")
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
    async def on_slash_command_error(_, ctx, error):
        """Error message handler."""
        unexpected = False
        title = "❌ Error"
        if isinstance(error, UserError):
            description = error.args[0]
        elif isinstance(error, commands.errors.CommandOnCooldown):
            description = f"This command is on cooldown. Please try again in `{error.retry_after:.2f}s`."
        else:
            unexpected = True
            description = (
                "An unexpected error occured. Please contact the bot developer."
            )
        embed = discord.Embed(title=title, description=description, color=0xCC0000)
        await ctx.send(embed=embed)
        if unexpected:
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
