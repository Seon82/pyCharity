import os
import asyncio
import logging
from dotenv import load_dotenv
from handlers.pxls import Canvas
from handlers.database import TemplateManager, StatsManager
from handlers.imgur_uploader import ImgurUploader
from handlers.websocket import WebsocketClient

logger = logging.getLogger("pyCharity." + __name__)
logger.info("Setting up...")
load_dotenv()

# Guild_ids
guild_ids = os.getenv("TEST_GUILD_ID", "")
if len(guild_ids) > 0:
    GUILD_IDS = [int(id) for id in guild_ids.split(",")]
else:  # Empty string
    print("No guild id specified: commands will be updated globally")
    GUILD_IDS = None

# Embed color
EMBED_COLOR = int(os.getenv("EMBED_COLOR"), 16)

# Invite link
invite_url = os.getenv("INVITE_LINK")

# Canvas
base_url = os.getenv("PXLS_URL")
canvas = Canvas(base_url=base_url)
asyncio.get_event_loop().run_until_complete(canvas.setup())

# Template manager
template_manager = TemplateManager(os.getenv("DB_CONNECTION"))

# Stats manager
stats_manager = StatsManager(os.getenv("DB_CONNECTION"))

# Websocket
ws_client = WebsocketClient(uri=os.getenv("PXLS_WEBSOCKET"), canvas=canvas)
ws_client.start()

# Imgur client
image_uploader = ImgurUploader(os.getenv("IMGUR_CLIENT_ID"))
