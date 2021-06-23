import math
from urllib.parse import urljoin
import aiohttp
from handlers import base_url


class BadResponseError(Exception):
    pass


async def json_query(endpoint: str):
    """Send a GET request to the endpoint and return the json content of the reponse."""
    async with aiohttp.ClientSession() as session:
        async with session.get(urljoin(base_url, endpoint)) as response:
            if response.status == 200:
                return await response.json()
            raise BadResponseError("Query returned {r.status} code.")


async def get_users():
    """Get the number of online users."""
    response_json = await json_query("users")
    return response_json["count"]


async def cooldown(num_users: int):
    """Get the cooldown when num_users users are online."""
    return 2.5 * math.sqrt(num_users + 11.96) + 6.5
