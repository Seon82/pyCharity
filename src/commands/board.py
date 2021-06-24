import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands import guild_ids, canvas
from handlers.discord_utils import attach_image


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="board",
        description="Show current board.",
        guild_ids=guild_ids,
    )
    async def _board(self, ctx: SlashContext):
        image = await canvas.board.render(canvas.palette)
        embed = discord.Embed(title="Board")
        file = attach_image(image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
