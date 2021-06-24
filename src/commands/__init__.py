import os
from dotenv import load_dotenv
from handlers.pxls.canvas import Canvas

load_dotenv()

guild_id = os.getenv("TEST_GUILD_ID", "")
if len(guild_id) > 0:
    guild_ids = [int(guild_id)]
else:  # Empty string
    guild_ids = None

base_url = os.getenv("PXLS_URL")
canvas = Canvas(base_url=base_url)
