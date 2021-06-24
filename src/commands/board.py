import io
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands import guild_ids, canvas


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="board",
        description="Show current board.",
        guild_ids=guild_ids,
    )
    async def _board(self, ctx: SlashContext):
        image = canvas.board
        embed = discord.Embed(title="Board")
        with io.BytesIO() as buffer:
            image.save(buffer, format="png", compression_level=6)
            buffer.seek(0)
            file = discord.File(buffer, filename="board.png")
            embed.set_image(url="attachment://board.png")
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
