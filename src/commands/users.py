from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands import guild_ids, canvas


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="users",
        description="Get number of online users",
        guild_ids=guild_ids,
    )
    async def _users(self, ctx: SlashContext):
        users = await canvas.get_users()
        await ctx.send(f"{users} users currently online.")


def setup(bot):
    bot.add_cog(Slash(bot))
