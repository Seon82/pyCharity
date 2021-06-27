import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from main import GUILD_IDS, canvas, EMBED_COLOR
from handlers.discord_utils import attach_image


class Board(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="board",
        description="Show current board.",
        guild_ids=GUILD_IDS,
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _board(self, ctx: SlashContext):
        image = await canvas.board.render(canvas.palette)
        embed = discord.Embed(title="Board", color=EMBED_COLOR)
        file = attach_image(image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Board(bot))
