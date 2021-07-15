from io import BytesIO
import aiohttp
import numpy as np
from handlers.pxls.utils import BadResponseError
from handlers.image import image2buffer


class ImgurUploader:
    """
    An object simplifying image uploads to imgur.
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.headers = {"Authorization": f"Client-ID {self.client_id}"}

    async def upload_image(self, image: np.ndarray) -> str:
        """
        Upload a rgba image array to imgur.
        """
        buffer = image2buffer(image)
        link = await self.upload_data(buffer)
        return link

    async def upload_data(self, data: BytesIO):
        """
        Upload binary data representing an image file.
        """
        url = "https://api.imgur.com/3/image/"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data={"image": data.getvalue()}, headers=self.headers
            ) as response:
                if response.status != 200:
                    raise BadResponseError("Query returned {response.status} code.")
                response_content = await response.json()
                return response_content["data"]["link"]
