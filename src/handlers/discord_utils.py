import io
import asyncio
from typing import Optional, Dict, List
import discord
from discord_slash.context import ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from PIL import Image
from .pxls.utils import Progress


class UserError(Exception):
    """
    Exception used to notify the user of an error.
    Will be caught by the error handler and broadcasted
    back at them as a message.
    """


def attach_image(
    image: Image.Image, embed: discord.Embed, compression_level: int = 6
) -> discord.File:
    """
    Attach a PIL image to a discord embed.

    :param image: The image to attach.
    :param embed: The embed it should be attached to.
    :param compression_level: The compression level PIL should use when saving oh png.
    :return: A discord.file object that should be sent with the embed.
    """
    with io.BytesIO() as buffer:
        image.save(buffer, format="png", compression_level=compression_level)
        buffer.seek(0)
        file = discord.File(buffer, filename="image.png")
        embed.set_image(url="attachment://image.png")
    return file


async def get_owner_name(scope, owner_id, bot):
    """
    Get the owner's name.
    """
    if scope == "faction":
        owner = await bot.fetch_guild(owner_id)
        owner_name = owner.name
    else:
        owner = await bot.fetch_user(owner_id)
        owner_name = f"{owner.name}#{owner.discriminator}"

    return owner_name


async def template_preview(template, bot, canvas, embed_color):
    """
    Generate an template preview embed.
    """
    owner_name = await get_owner_name(template.scope, template.owner, bot)
    embed = discord.Embed(
        title=template.name,
        description=f"**Owner:** {owner_name}\n**Progress:** {template.progress.percentage:.1f}%",
        color=embed_color,
        url=template.url,
    )
    template_img = await template.render(canvas.palette)
    file = attach_image(template_img, embed)
    return file, embed


def button(
    label: str,
    custom_id: Optional[str] = None,
    style: str = "blurple",
):
    """
    Create and return a button component.
    :param label: The button's label.
    :param custom_id: The button's unique identifier.
    :param style: A ButtonStyle attribute.
    """
    return manage_components.create_button(
        style=getattr(ButtonStyle, style), label=label, custom_id=custom_id
    )


async def ask_alternatives(ctx, bot, buttons: list, timeout: int = 20, **kwargs):
    """
    Ask a  question.
    """
    action_row = manage_components.create_actionrow(*buttons)
    if isinstance(ctx, ComponentContext):
        sender = ctx.edit_origin
    else:
        sender = ctx.send
    await sender(
        **kwargs,
        components=[action_row],
    )
    try:
        button_ctx = await manage_components.wait_for_component(
            bot, components=action_row, timeout=timeout
        )
    except asyncio.TimeoutError:
        raise UserError("Timed out.")
    return button_ctx


async def render_list(bot, templates: List[Dict[str, list]], embed_color: int):
    """
    Generate an embed representing a template list.

    :param templates: A dictionary mapping category names
    to lists of template info (dicts).
    """
    total_description = ""
    for scope in templates.keys():
        if len(templates[scope]) > 0:
            total_description += f"**{scope.capitalize()} templates**:\n"
            for template in templates[scope]:
                owner_name = await get_owner_name(scope, template["owner"], bot)
                progress = round(Progress(**template["progress"]).percentage, 1)
                total_description += (
                    f"• **[{template['name']}]({template['url']})**"
                    f" ({progress}%), by {owner_name}\n"
                )
    if total_description == "":
        total_description = "No templates are being tracked yet."
    embed = discord.Embed(color=embed_color, description=total_description)
    return embed
