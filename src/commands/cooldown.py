import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands import guild_ids, canvas, embed_color
from handlers.pxls.utils import cooldown


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="cooldown",
        description="Get current cooldown.",
        guild_ids=guild_ids,
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _cooldown(self, ctx: SlashContext):
        users = await canvas.get_users()
        current_cooldown = cooldown(users)
        embed = discord.Embed(
            title="⏳ Cooldown info",
            description=f"Cooldown is currently {round(current_cooldown)}s.",
            color=embed_color,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
