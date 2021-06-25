import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands import guild_ids, embed_color


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="Pong!", guild_ids=guild_ids)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _ping(self, ctx: SlashContext):
        latency = self.bot.latency
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"{self.bot.user.name}'s ping is `{round(latency * 1000)} ms`.",
            color=embed_color,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
