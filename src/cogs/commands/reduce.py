import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from main import GUILD_IDS, canvas, EMBED_COLOR
from handlers.discord_utils import attach_image
from handlers.pxls import Template, PalettizedImage
from handlers.pxls.utils import download_image


class Reduce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="reduce",
        description="Colorize an image to fit pxls' palette.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="url",
                description="Image link.",
                option_type=3,
                required=True,
            )
        ],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _reduce(self, ctx: SlashContext, url: str):
        await ctx.defer()
        image = await download_image(url)
        recolored_array = await Template.reduce(image, canvas.palette)
        recolored_image = await PalettizedImage(recolored_array).render(canvas.palette)
        embed = discord.Embed(title="Reduced!", color=EMBED_COLOR)
        file = attach_image(recolored_image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Reduce(bot))
