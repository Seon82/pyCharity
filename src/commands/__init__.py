import os
from dotenv import load_dotenv

load_dotenv()
guild_id = os.getenv("TEST_GUILD_ID", "")
if len(guild_id) > 0:
    guild_ids = [int(guild_id)]
else:  # Empty string
    guild_ids = None
