import io
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
