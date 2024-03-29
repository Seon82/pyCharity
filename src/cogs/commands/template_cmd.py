from typing import Optional, Dict, List
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from handlers.setup import GUILD_IDS, canvas, template_manager, EMBED_COLOR
from handlers.discord_utils import (
    render_list,
    UserError,
    template_preview,
    button,
    ask_alternatives,
)
from handlers.pxls import Template, BaseTemplate, utils

url_option = create_option(
    name="url",
    description="pxls.space template link.",
    option_type=3,
    required=True,
)

name_option = create_option(
    name="name",
    description="Template name.",
    option_type=3,
    required=True,
)

sort_option = create_option(
    name="sort",
    description="Sort by progress order: '% up', '% down' or 'pixels left'",
    option_type=3,
    required=False,
    choices=["% up", "% down", "pixels left"],
)


class TemplateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="template",
        name="add",
        guild_ids=GUILD_IDS,
        description="Add a template to the tracker.",
        options=[name_option, url_option],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _add(self, ctx: SlashContext, name: str, url: str):
        await ctx.defer()
        if not utils.check_template_link(url):
            raise UserError("Please provide a valid template link.")
        # Check if a template with the same name exists.
        if await template_manager.check_name_exists(name, canvas_code=canvas.code):
            raise UserError(
                "A template with this name already exists."
                "If it doesn't appear in the global tracker, it means it's private."
            )
        if name == "combo":
            raise UserError("This name is reserved.")
        base_template = await BaseTemplate.from_url(url, canvas=canvas)
        question = f"Should I add `{name}` to the public tracker?"
        buttons = [
            button("Make it public", "global"),
            button("Keep it private", "private"),
        ]
        button_ctx = await ask_alternatives(ctx, self.bot, buttons, content=question)
        if (
            button_ctx.component_id == "global"
            and ctx.guild
            and ctx.author.guild_permissions.manage_guild
        ):
            question = "Is this a personal project?"
            buttons = [
                button("Personal project", "global"),
                button("Faction project", "faction"),
            ]
            button_ctx = await ask_alternatives(
                button_ctx, self.bot, buttons, content=question
            )
        await button_ctx.edit_origin(content="Almost done...", components=[])
        scope = button_ctx.component_id
        owner = ctx.guild_id if scope == "faction" else ctx.author_id
        template = await Template.from_base(
            base_template, name, url, canvas, owner, scope
        )
        await template_manager.add_template(template)
        file, embed = await template_preview(template, self.bot, canvas, EMBED_COLOR)
        await ctx.message.edit(content="", file=file, embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="update",
        guild_ids=GUILD_IDS,
        description="Change the link for a template already in the tracker.",
        options=[name_option, url_option],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _update(self, ctx: SlashContext, name: str, url: str):
        await ctx.defer()
        if not utils.check_template_link(url):
            raise UserError("Please provide a valid template link.")
        template = await template_manager.get_template(
            no_image=True, name=name, canvas_code=canvas.code
        )
        self._check_permissions(ctx, template)
        template = await Template.from_url(
            url,
            name=name,
            owner=template.owner,
            canvas=canvas,
            scope=template.scope,
        )
        await template_manager.update_template(template)
        file, embed = await template_preview(template, self.bot, canvas, EMBED_COLOR)
        await ctx.send(file=file, embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="remove",
        guild_ids=GUILD_IDS,
        description="Remove a template from the tracker.",
        options=[name_option],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _remove(self, ctx: SlashContext, name: str):
        # Only fetch the metadata and not the image
        template = await template_manager.get_template(
            no_image=True, name=name, canvas_code=canvas.code
        )
        self._check_permissions(ctx, template)
        success = await template_manager.delete_template(
            name=name,
            owner=template.owner,
            canvas_code=canvas.code,
        )
        if not success:
            raise UserError("Deletion failed. Please contact the bot developer.")
        embed = discord.Embed(
            title="Deleted!",
            description=f"Successfully deleted `{name}` from the tracker.",
            color=EMBED_COLOR,
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="list",
        guild_ids=GUILD_IDS,
        description="Display all currently tracked templates.",
        options=[sort_option],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _list(self, ctx: SlashContext, sort: Optional[str] = None):
        await ctx.defer()
        display_progress_pixels = False
        if not sort is None:
            if sort in ["% up", "% down"]:
                sorter = lambda template: template.progress.percentage
                reverse_order = sort == "down"
            elif sort == "pixels left":
                sorter = lambda template: template.progress.remaining
                reverse_order = True
                display_progress_pixels = True

        scopes = ["private", "global", "faction"]
        templates: Dict[str, List[Template]] = {scope: [] for scope in scopes}
        # Only fetch the metadata and not the image
        template_generator = template_manager.get_templates(
            no_image=True, canvas_code=canvas.code
        )
        async for template in template_generator:
            if (
                template.scope == "private"
                and ctx.author_id == template.owner
                and ctx.guild is None
            ):  # In DMs
                templates["private"].append(template)
            elif template.scope == "faction" and ctx.guild_id == template.owner:
                templates["faction"].append(template)
            elif template.scope != "private":
                if template.name == "combo":  # Show combo first
                    templates["global"].insert(0, template)
                else:
                    templates["global"].append(template)
        if sort:
            templates = {
                scope: sorted(temps, key=sorter, reverse=reverse_order)
                for scope, temps in templates.items()
            }
        embed = await render_list(
            self.bot, templates, display_progress_pixels, EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="show",
        guild_ids=GUILD_IDS,
        description="Display a template from the tracker.",
        options=[name_option],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _show(self, ctx: SlashContext, name: str):
        await ctx.defer()
        template = await template_manager.get_template(
            name=name, canvas_code=canvas.code
        )
        if template is None:
            raise UserError("Invalid template name.")
        if template.scope == "private" and ctx.author_id != template.owner:
            raise UserError("This template is private.")
        file, embed = await template_preview(template, self.bot, canvas, EMBED_COLOR)
        await ctx.send(file=file, embed=embed)

    @staticmethod
    def _check_permissions(ctx: SlashContext, template: Template):
        """
        Check whether a user has permissions over a template.
        Raises a UserError if they don't, returns None otherwise.

        :param ctx: The author's command SlashContext.
        :param template: A template.
        """
        if template is None:
            raise UserError("Invalid template name.")
        scope, owner = template.scope, template.owner
        if scope == "faction" and ctx.guild is None:
            raise UserError("A faction template can't be managed from DMs.")
        if scope == "faction" and ctx.guild.id != owner:
            raise UserError("This template doesn't belong to this server.")
        if scope == "faction" and not ctx.author.guild_permissions.manage_guild:
            raise UserError(
                "You do not have the permission to manage faction templates."
            )
        if scope in ["private", "global"] and ctx.author.id != owner:
            raise UserError("This template doesn't belong to you.")


def setup(bot):
    bot.add_cog(TemplateCommand(bot))
