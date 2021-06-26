import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from main import GUILD_IDS, canvas, EMBED_COLOR
from handlers.pxls.utils import cooldown


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="cooldown",
        description="Get current cooldown.",
        guild_ids=GUILD_IDS,
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _cooldown(self, ctx: SlashContext):
        users = await canvas.fetch_users()
        current_cooldown = cooldown(users)
        embed = discord.Embed(
            title="⏳ Cooldown info",
            description=f"Cooldown is currently {round(current_cooldown)}s.",
            color=EMBED_COLOR,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
