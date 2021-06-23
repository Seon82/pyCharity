from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from handlers.pxls import cooldown, get_users
from commands import guild_ids


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="cooldown",
        description="Get current cooldown.",
        guild_ids=guild_ids,
    )
    async def _cooldown(self, ctx: SlashContext):
        users = await get_users()
        current_cooldpwn = await cooldown(users)
        await ctx.send(f"Cooldown is currently {current_cooldpwn:.0f}s.")


def setup(bot):
    bot.add_cog(Slash(bot))
