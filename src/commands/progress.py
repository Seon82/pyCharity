import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from main import GUILD_IDS, canvas, EMBED_COLOR, template_manager
from handlers.discord_utils import UserError, attach_image
from handlers.pxls import utils, BaseTemplate, PalettizedImage


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="progress",
        description="Check a template's progress.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name=f"template",
                description="Template name or link.",
                option_type=3,
                required=True,
            )
        ],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _progress(self, ctx: SlashContext, template: str):
        await ctx.defer()
        template_name = template
        if utils.check_template_link(template_name):
            template = await BaseTemplate.from_url(template_name, canvas)
        else:
            template = await template_manager.get_template(name=template_name)
            if template is None:
                raise UserError(f"{template_name} isn't a valid template name.")
        progress_array, (completed_pixels, total_pixels) = await utils.progress(
            canvas=canvas, template=template
        )
        image = await PalettizedImage(progress_array).render(
            [(255, 0, 0, 255), (0, 255, 0, 255)]
        )
        description = f"{100*completed_pixels/total_pixels:.1f}% complete ({completed_pixels}/{total_pixels} pixels)."
        embed = discord.Embed(
            title="Progress", description=description, color=EMBED_COLOR
        )
        file = attach_image(image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
