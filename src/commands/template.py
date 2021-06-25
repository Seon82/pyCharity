import discord
from discord.ext import commands
from discord.message import Message
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from commands import guild_ids, canvas, template_manager
from handlers.discord_utils import attach_image, UserError
from handlers.pxls import Template

url_option = create_option(
    name="url",
    description="pxls.space template link.",
    option_type=3,
    required=True,
)

name_option = create_option(
    name="name",
    description="template name.",
    option_type=3,
    required=True,
)


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="template",
        name="add",
        guild_ids=guild_ids,
        description="Add a template to the tracker.",
        options=[name_option, url_option],
    )
    async def _add(self, ctx: SlashContext, name: str, url: str):
        await ctx.defer()
        if template_manager.check_name_exists(name, owner=ctx.guild_id):
            raise UserError("A template with this name already exists.")
        template = await Template.from_url(
            url, name=name, owner=ctx.guild_id, palette=canvas.palette
        )
        template_manager.add_template(template)
        embed = discord.Embed(
            title=name, description=f"[{template.url}]({template.url})"
        )
        template_img = await template.render(canvas.palette)
        file = attach_image(template_img, embed)
        await ctx.send(file=file, embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="remove",
        guild_ids=guild_ids,
        description="Remove a template from the tracker.",
        options=[name_option],
    )
    async def _remove(self, ctx: SlashContext, name: str):
        success = template_manager.delete_template(name=name, owner=ctx.guild_id)
        if not success:
            raise UserError("Invalid template name.")
        embed = discord.Embed(
            title="Deleted!",
            description=f"Successfully deleted {name} from the tracker.",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="list",
        guild_ids=guild_ids,
        description="Display all currently tracked templates.",
    )
    async def _list(self, ctx: SlashContext):
        templates = template_manager.get_templates(owner=ctx.guild_id)
        embed = discord.Embed(title="Template list:")
        for template in templates:
            embed.add_field(
                name=template.name,
                value=f"[{template.url}]({template.url})",
                inline=False,
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="show",
        guild_ids=guild_ids,
        description="Display a template from the tracker.",
        options=[name_option],
    )
    async def _show(self, ctx: SlashContext, name: str):
        await ctx.defer()
        template = template_manager.get_template(name=name, owner=ctx.guild_id)
        if template is None:
            raise UserError("Invalid template name.")
        embed = discord.Embed(
            title=name, description=f"[{template.url}]({template.url})"
        )
        template_img = await template.render(canvas.palette)
        file = attach_image(template_img, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
