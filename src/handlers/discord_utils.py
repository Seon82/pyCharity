import asyncio
from typing import Optional, Dict, List
import discord
from discord_slash.context import ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
import numpy as np
from handlers.image import image2buffer
from .pxls import Progress


class UserError(Exception):
    """
    Exception used to notify the user of an error.
    Will be caught by the error handler and broadcasted
    back at them as a message.
    """


def attach_image(image: np.ndarray, embed: discord.Embed) -> discord.File:
    """
    Attach a rgba image array to a discord embed.

    :param image: The image to attach.
    :param embed: The embed it should be attached to.
    :return: A discord.file object that should be sent with the embed.
    """
    buffer = image2buffer(image)
    file = discord.File(buffer, filename="image.png")
    embed.set_image(url="attachment://image.png")
    return file


async def get_owner_name(scope, owner_id, bot):
    """
    Get the owner's name.
    """
    if scope == "faction":
        try:
            owner = await bot.fetch_guild(owner_id)
            owner_name = owner.name
        except discord.errors.Forbidden:  # pycharity's been kicked from the server
            owner_name = "_an unknown faction_"
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
    label: str, custom_id: Optional[str] = None, style: str = "blurple", **kwargs
):
    """
    Create and return a button component.
    :param label: The button's label.
    :param custom_id: The button's unique identifier.
    :param style: A ButtonStyle attribute.
    """
    return manage_components.create_button(
        style=getattr(ButtonStyle, style), label=label, custom_id=custom_id, **kwargs
    )


async def ask_alternatives(
    ctx, bot, buttons: list, timeout: int = 20, raise_error=True, **kwargs
):
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
        return button_ctx
    except asyncio.TimeoutError:
        if raise_error:
            raise UserError("Timed out.")
        await ctx.message.edit(components=[])


async def render_list(
    bot,
    templates: List[Dict[str, list]],
    display_progress_pixels: bool,
    embed_color: int,
):
    """
    Generate an embed representing a template list.

    :param templates: A dictionary mapping category names
    to lists of template info (dicts).
    :param display_progress_pixels: Whether to display progress as a pixel count
    or a percentage.
    """
    total_description = ""
    for scope in templates.keys():
        if len(templates[scope]) > 0:
            total_description += f"**{scope.capitalize()} templates**:\n"
            for template in templates[scope]:
                owner_name = await get_owner_name(
                    template["scope"], template["owner"], bot
                )
                if display_progress_pixels:
                    progress = Progress(**template["progress"])
                    progress_txt = f"{progress.remaining} left"
                else:
                    progress_txt = f"{Progress(**template['progress']).percentage:.1f}%"
                total_description += (
                    f"• **[{template['name']}]({template['url']})**"
                    f" ({progress_txt}), by {owner_name}\n"
                )
            total_description += "\n"
    if total_description == "":
        total_description = "No templates are being tracked yet."
    embed = discord.Embed(color=embed_color, description=total_description)
    return embed
