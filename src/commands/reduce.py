import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from commands import guild_ids, canvas
from handlers.discord_utils import attach_image
from handlers.pxls.template import Template
from handlers.pxls.utils import download_image
from handlers.pxls.image import PalettizedImage


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="reduce",
        description="Colorize an image to fit pxls' palette.",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="url",
                description="Image link.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _reduce(self, ctx: SlashContext, url: str):
        await ctx.defer()
        image = await download_image(url)
        recolored_array = await Template.reduce(image, canvas.palette)
        recolored_image = await PalettizedImage(recolored_array).render(canvas.palette)
        embed = discord.Embed(title="Reduced image")
        file = attach_image(recolored_image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
