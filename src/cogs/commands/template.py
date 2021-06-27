import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from main import GUILD_IDS, canvas, template_manager, EMBED_COLOR
from handlers.discord_utils import (
    get_owner_name,
    UserError,
    template_preview,
    attach_image,
)
from handlers.pxls import Template, utils

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

faction_option = create_option(
    name="faction",
    description="Make the template a faction template.",
    option_type=5,
    required=False,
)


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="template",
        name="add",
        guild_ids=GUILD_IDS,
        description="Add a template to the tracker.",
        options=[name_option, url_option, faction_option],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _add(self, ctx: SlashContext, name: str, url: str, faction: bool = False):
        await ctx.defer()
        if not utils.check_template_link(url):
            raise UserError("Please provide a valid template link.")
        if faction and not ctx.author.guild_permissions.manage_guild:
            raise UserError(
                "You do not have the permission to manage faction templates."
            )
        # Check if a template with the same name exists.
        if await template_manager.check_name_exists(
            name, canvas_code=canvas.info["canvasCode"]
        ):
            raise UserError("A template with this name already exists.")
        scope = "faction" if faction else "user"
        owner = ctx.guild if scope == "faction" else ctx.author
        template = await Template.from_url(
            url, name=name, owner=owner.id, canvas=canvas, scope=scope
        )
        await template_manager.add_template(template)
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
        # Faster query by only fetching the metadata and not the image
        template_info = await template_manager.find_one(
            name=name, projection={"image": False}
        )
        if template_info is None:
            raise UserError("Invalid template name.")
        scope, owner = template_info["scope"], template_info["owner"]
        if scope == "faction" and ctx.guild.id != owner:
            raise UserError(f"This template doesn't belong to this server.")
        if scope == "faction" and not ctx.author.guild_permissions.manage_guild:
            raise UserError(
                "You do not have the permission to manage faction templates."
            )
        if scope == "user" and ctx.author.id != owner:
            raise UserError("This template doesn't belong to you.")
        success = await template_manager.delete_template(
            name=name, owner=owner, canvas_code=canvas.info["canvasCode"]
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
        embed = discord.Embed(color=EMBED_COLOR)
        faction_description = ""
        global_description = ""
        template_info = template_manager.find(
            projection={"image": False}, canvas_code=canvas.info["canvasCode"]
        )
        async for info in template_info:
            owner_name = await get_owner_name(info["scope"], info["owner"], self.bot)
            description = f"• **[{info['name']}]({info['url']})**, by {owner_name}\n"
            if info["scope"] == "faction" and info["owner"] == ctx.guild.id:
                faction_description += description
            else:
                global_description += description

        # Combine bothe faction and global description
        total_description = ""
        if len(faction_description) > 0:
            total_description += f"**Faction templates:**\n {faction_description}\n\n"
        total_description += "**Global templates:**\n"
        if len(global_description) > 0:
            total_description += global_description
        else:
            total_description += "No templates are being tracked yet."
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
        file, embed = await template_preview(template, self.bot, canvas, EMBED_COLOR)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
