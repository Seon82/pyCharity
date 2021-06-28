import io
import importlib
import discord
from PIL import Image


class UserError(Exception):
    pass


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
    if scope == "user":
        owner = await bot.fetch_user(owner_id)
        owner_name = f"{owner.name}#{owner.discriminator}"
    else:
        owner = await bot.fetch_guild(owner_id)
        owner_name = owner.name
    return owner_name


async def template_preview(template, bot, canvas, embed_color):
    """
    Generate an template preview embed.
    """
    owner_name = await get_owner_name(template.scope, template.owner, bot)
    embed = discord.Embed(
        title=template.name,
        description=f"**Owner:** {owner_name}\n**Link:** {template.url}",
        color=embed_color,
    )
    template_img = await template.render(canvas.palette)
    file = attach_image(template_img, embed)
    return file, embed
