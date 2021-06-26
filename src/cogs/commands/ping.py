import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from main import GUILD_IDS, EMBED_COLOR


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="Pong!", guild_ids=GUILD_IDS)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _ping(self, ctx: SlashContext):
        latency = self.bot.latency
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"{self.bot.user.name}'s ping is `{round(latency * 1000)} ms`.",
            color=EMBED_COLOR,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
