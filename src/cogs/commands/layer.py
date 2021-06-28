import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from handlers.setup import GUILD_IDS, canvas, EMBED_COLOR, template_manager
from handlers.discord_utils import UserError, attach_image
from handlers.pxls import utils, BaseTemplate


class LayerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="layer",
        description="Combine multiple templates",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name=f"template{i}",
                description="Template name or link.",
                option_type=3,
                required=i < 2,
            )
            for i in range(5)
        ],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _layer(self, ctx: SlashContext, **template_names):
        await ctx.defer()
        templates = []
        for template_name in template_names.values():
            if utils.check_template_link(template_name):
                template = await BaseTemplate.from_url(template_name, canvas)
            else:
                template = await template_manager.get_template(
                    name=template_name, canvas_code=canvas.info["canvasCode"]
                )
                if template is None:
                    raise UserError(f"{template_name} isn't a valid template name.")
            templates.append(template)
        palettized_image = await utils.layer(
            canvas.board.width, canvas.board.height, *templates
        )
        image = await palettized_image.render(canvas.palette)
        embed = discord.Embed(title="Layered!", color=EMBED_COLOR)
        file = attach_image(image, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(LayerCommand(bot))
