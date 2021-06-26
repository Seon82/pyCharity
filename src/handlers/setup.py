import os
from handlers.pxls import Canvas, TemplateManager
from dotenv import load_dotenv


async def setup():
    """
    Initialize objects.
    """
    load_dotenv()
    guild_id = os.getenv("TEST_GUILD_ID", "")
    if len(guild_id) > 0:
        guild_ids = [int(guild_id)]
    else:  # Empty string
        guild_ids = None

    embed_color = int(os.getenv("EMBED_COLOR"), 16)
    base_url = os.getenv("PXLS_URL")
    canvas = Canvas(base_url=base_url)
    await canvas.setup()

    template_manager = TemplateManager(os.getenv("DB_CONNECTION"))

    return guild_ids, canvas, template_manager, embed_color
