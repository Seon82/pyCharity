import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from handlers.setup import GUILD_IDS, canvas, EMBED_COLOR, template_manager
from handlers.discord_utils import UserError, attach_image
from handlers.pxls import utils, BaseTemplate, compute_progress
from handlers.image import PalettizedImage


class ProgressCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="progress",
        description="Check a template's progress.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="template",
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
            template = await template_manager.get_template(
                name=template_name, canvas_code=canvas.code
            )
            if template is None:
                raise UserError(f"`{template_name}` isn't a valid template name.")
            if template.scope == "private" and ctx.author_id != template.owner:
                raise UserError("This template is private.")
        progress = await compute_progress(
            canvas=canvas, template=template, compute_array=True
        )
        image = await PalettizedImage(progress.array).render(
            [(255, 0, 0, 255), (0, 255, 0, 255), (70, 70, 70, 100)]
        )
        description = (
            f"{progress.percentage:.1f}% complete"
            f" ({progress.correct}/{progress.total} pixels)."
        )
        embed = discord.Embed(
            title="Progress", description=description, color=EMBED_COLOR
        )
        file = attach_image(image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(ProgressCommand(bot))
