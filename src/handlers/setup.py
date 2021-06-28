import os
from handlers.pxls import Canvas, TemplateManager
from dotenv import load_dotenv
from handlers.websocket import WebsocketClient


async def setup():
    """
    Initialize objects.
    """
    load_dotenv()
    guild_ids = os.getenv("TEST_GUILD_ID", "")
    if len(guild_ids) > 0:
        guild_ids = [int(id) for id in guild_ids.split(",")]
    else:  # Empty string
        print("No guild id specified: commands will be updated globally")
        guild_ids = None

    embed_color = int(os.getenv("EMBED_COLOR"), 16)
    base_url = os.getenv("PXLS_URL")
    canvas = Canvas(base_url=base_url)
    await canvas.setup()

    template_manager = TemplateManager(os.getenv("DB_CONNECTION"))

    ws_client = WebsocketClient(uri=os.getenv("PXLS_WEBSOCKET"), canvas=canvas)
    ws_client.start()

    return guild_ids, canvas, template_manager, ws_client, embed_color
