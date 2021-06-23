from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands import guild_ids


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="ping",
        description="Pong!",
        guild_ids=guild_ids,
    )
    async def _ping(self, ctx: SlashContext):
        latency = self.bot.latency
        await ctx.send(f"Pong! {latency*1000:.2f}ms")


def setup(bot):
    bot.add_cog(Slash(bot))
