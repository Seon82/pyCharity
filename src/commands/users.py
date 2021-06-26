from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from main import GUILD_IDS, canvas


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="users",
        description="Get number of online users",
        guild_ids=GUILD_IDS,
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _users(self, ctx: SlashContext):
        users = await canvas.fetch_users()
        await ctx.send(f"{users} users currently online.")


def setup(bot):
    bot.add_cog(Slash(bot))
