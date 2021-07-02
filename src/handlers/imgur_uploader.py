import io
from PIL import Image
import aiohttp
from handlers.pxls.utils import BadResponseError


class ImgurUploader:
    """
    An object simplifying image uploads to imgur.
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.headers = {"Authorization": f"Client-ID {self.client_id}"}

    async def upload_image(self, image: Image.Image, compression_level: int = 6) -> str:
        """
        Upload a PIL image to imgur.
        """
        with io.BytesIO() as buffer:
            image.save(buffer, format="png", compression_level=compression_level)
            img_buffer = buffer.getvalue()
        link = await self.upload_data(img_buffer)
        return link

    async def upload_data(self, data: io.BytesIO):
        """
        Upload binary data representing an image file.
        """
        url = "https://api.imgur.com/3/image/"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data={"image": data}, headers=self.headers
            ) as response:
                if response.status != 200:
                    raise BadResponseError("Query returned {response.status} code.")
                response_content = await response.json()
                return response_content["data"]["link"]
