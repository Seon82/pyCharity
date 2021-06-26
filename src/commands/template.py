import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from main import GUILD_IDS, canvas, template_manager, EMBED_COLOR
from handlers.discord_utils import attach_image, UserError
from handlers.pxls import Template, utils

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
        guild_ids=GUILD_IDS,
        description="Add a template to the tracker.",
        options=[name_option, url_option],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _add(self, ctx: SlashContext, name: str, url: str):
        await ctx.defer()
        if not utils.check_template_link(url):
            raise UserError("Please provide a valid template link.")
        # Check if a template with the same name not owned by the user running the command exists.
        if await template_manager.check_name_exists(name, owner={"$ne": ctx.author_id}):
            raise UserError("A template with this name already exists.")
        template = await Template.from_url(
            url, name=name, owner=ctx.author_id, canvas=canvas
        )
        await template_manager.add_template(template)
        owner = await self.bot.fetch_user(template.owner)
        embed = discord.Embed(
            title=name,
            description=f"**Owner:** {owner.name}#{owner.discriminator}\n**Link:** {template.url}",
            color=EMBED_COLOR,
        )
        template_img = await template.render(canvas.palette)
        file = attach_image(template_img, embed)
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
        success = await template_manager.delete_template(name=name, owner=ctx.author_id)
        if not success:
            raise UserError("Invalid template name.")
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
        template_info = template_manager.find(projection={"image": False})
        embed = discord.Embed(title="Template list:", color=EMBED_COLOR)
        async for info in template_info:
            owner = await self.bot.fetch_user(info["owner"])
            embed.add_field(
                name=info["name"],
                value=f"Owner: {owner.name}#{owner.discriminator}\nLink: {info['url']}",
                inline=False,
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
        template = await template_manager.get_template(name=name)
        if template is None:
            raise UserError("Invalid template name.")
        owner = await self.bot.fetch_user(template.owner)
        embed = discord.Embed(
            title=name,
            description=f"**Owner:** {owner.name}#{owner.discriminator}\n**Link:** {template.url}",
            color=EMBED_COLOR,
        )
        template_img = await template.render(canvas.palette)
        file = attach_image(template_img, embed)
        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Slash(bot))
