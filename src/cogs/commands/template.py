import asyncio
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils import manage_components
from handlers.setup import GUILD_IDS, canvas, template_manager, EMBED_COLOR
from handlers.discord_utils import get_owner_name, UserError, template_preview, button
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
        if await template_manager.check_name_exists(
            name, canvas_code=canvas.info["canvasCode"]
        ):
            raise UserError("A template with this name already exists.")
        base_template = await BaseTemplate.from_url(url, canvas=canvas)
        buttons = [
            button("Global template", "global"),
            button("Private template", "private"),
        ]
        if ctx.guild and ctx.author.guild_permissions.manage_guild:
            buttons.insert(0, button("Faction template", "faction"))
        action_row = manage_components.create_actionrow(*buttons)
        msg = await ctx.send(
            f"Ready to add {name} to the tracker! What kind of template is it?",
            components=[action_row],
        )
        try:
            button_ctx = await manage_components.wait_for_component(
                self.bot, components=action_row, timeout=20
            )
        except asyncio.TimeoutError:
            raise UserError("Timed out.")
        await button_ctx.edit_origin(
            content=f"Adding {name} to the tracker...", components=[]
        )
        scope = button_ctx.component_id
        owner = ctx.guild_id if scope == "faction" else ctx.author_id
        template = Template.from_base(
            base_template, name, url, canvas.info["canvasCode"], owner, scope
        )
        await template_manager.add_template(template)
        file, embed = await template_preview(template, self.bot, canvas, EMBED_COLOR)
        await msg.edit(content="", file=file, embed=embed)

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
        template_info = await template_manager.find_one(
            name=name, projection={"image": False}
        )
        self._check_permissions(ctx, template_info)
        template = await Template.from_url(
            url,
            name=name,
            owner=template_info["owner"],
            canvas=canvas,
            scope=template_info["scope"],
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
        template_info = await template_manager.find_one(
            name=name, projection={"image": False}
        )
        self._check_permissions(ctx, template_info)
        success = await template_manager.delete_template(
            name=name,
            owner=template_info["owner"],
            canvas_code=canvas.info["canvasCode"],
        )
        if not success:
            raise UserError("Deletion failed. Please contact the bot developer.")
        embed = discord.Embed(
            title="Deleted!",
            description=f"Successfully deleted {name} from the tracker.",
            color=EMBED_COLOR,
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="template",
        name="list",
        guild_ids=GUILD_IDS,
        description="Display all currently tracked templates.",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _list(self, ctx: SlashContext):
        await ctx.defer()
        embed = discord.Embed(color=EMBED_COLOR)
        scopes = ["private", "global", "faction"]
        descriptions = {scope: "" for scope in scopes}
        # Only fetch the metadata and not the image
        template_info = template_manager.find(
            projection={"image": False}, canvas_code=canvas.info["canvasCode"]
        )
        async for info in template_info:
            scope, owner = info["scope"], info["owner"]
            owner_name = await get_owner_name(scope, owner, self.bot)
            description = f"• **[{info['name']}]({info['url']})**, by {owner_name}\n"
            if scope == "private" and ctx.guild is None:  # In DMs
                descriptions["private"] += description
            elif scope == "faction" and ctx.guild_id == owner:
                descriptions["faction"] += description
            elif scope != "private":
                descriptions["global"] += description

        # Combine all descriptions
        total_description = ""
        for header in scopes:
            if len(descriptions[header]) > 0:
                total_description += f"**{header.capitalize()} templates**:\n"
                total_description += descriptions[header] + "\n"
        if total_description == "":
            total_description = "No templates are being tracked yet."
        embed.description = total_description
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
            name=name, canvas_code=canvas.info["canvasCode"]
        )
        if template is None:
            raise UserError("Invalid template name.")
        if template.scope == "private" and ctx.author_id != template.owner:
            raise UserError("This template is private.")
        file, embed = await template_preview(template, self.bot, canvas, EMBED_COLOR)
        await ctx.send(file=file, embed=embed)

    @staticmethod
    def _check_permissions(ctx: SlashContext, template_info: dict):
        """
        Check whether a user has permissions over a template.
        Raises a UserError if they don't, returns None otherwise.

        :param ctx: The author's command SlashContext.
        :param template_info: A dictionary containing
        at least 'owner' and 'scope' information.
        """
        if template_info is None:
            raise UserError("Invalid template name.")
        scope, owner = template_info["scope"], template_info["owner"]
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
