import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from handlers.setup import GUILD_IDS, EMBED_COLOR
from handlers.discord_utils import attach_image, UserError
from handlers.pxls import Template, utils


class DetemplatizeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="detemplatize",
        description="Get the origin image from a template.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="url",
                description="pxls.space template link.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _detemplatize(self, ctx: SlashContext, url: str):
        await ctx.defer()
        if not utils.check_template_link(url):
            raise UserError("Please provide a valid template link.")
        params, styled_image = await Template.process_link(url)
        original_image = await Template.detemplatize(styled_image, int(params["tw"][0]))
        embed = discord.Embed(title="Detemplatized image", color=EMBED_COLOR)
        file = attach_image(original_image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(DetemplatizeCommand(bot))
