import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow
from handlers.setup import (
    GUILD_IDS,
    canvas,
    EMBED_COLOR,
    template_manager,
    image_uploader,
    base_url,
)
from handlers.discord_utils import UserError, ask_alternatives, attach_image, button
from handlers.pxls import utils, BaseTemplate, layer


class LayerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # pylint: disable = too-many-locals
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
        layered_template = await layer.layer(
            canvas.board.width, canvas.board.height, *templates
        )
        image = await layered_template.render(canvas.palette)
        embed = discord.Embed(title="Layered!", color=EMBED_COLOR)
        file = attach_image(image, embed)
        buttons = [button("Generate template link")]
        button_pressed = await ask_alternatives(
            ctx, self.bot, buttons, raise_error=False, file=file, embed=embed
        )
        if button_pressed:
            styled_image = await utils.style_dotted(image)
            styled_url = await image_uploader.upload_image(styled_image)
            url = utils.generate_template_url(layered_template, base_url, styled_url)
            url_button = button("Template link", style="URL", url=url)
            await button_pressed.edit_origin(components=[create_actionrow(url_button)])


def setup(bot):
    bot.add_cog(LayerCommand(bot))
