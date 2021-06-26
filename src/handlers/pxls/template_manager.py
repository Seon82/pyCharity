import pickle
from bson.binary import Binary
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from .template import Template


class TemplateManager:
    def __init__(self, mongo_uri: str):
        mongo_client = AsyncIOMotorClient(mongo_uri)
        self.collection = mongo_client.pycharity.templates

    @staticmethod
    def serialize(array: np.ndarray) -> Binary:
        return Binary(pickle.dumps(array, protocol=2), subtype=128)

    @staticmethod
    def deserialize(data: Binary) -> np.ndarray:
        return pickle.loads(data)

    async def add_template(self, template: Template):
        """
        Add a template to the database.
        """
        data = {
            "name": template.name,
            "owner": template.owner,
            "ox": template.ox,
            "oy": template.oy,
            "url": template.url,
            "image": self.serialize(template.image),
        }
        await self.collection.insert_one(data)

    async def get_template(self, **query) -> Template:
        """
        Find a template in the database matching the query.
        ex: self.get_template(name='Seon', owner=123456789)
        """
        document = await self.collection.find_one(query, {"_id": False})
        if document is None:
            return None
        array = self.deserialize(document.pop("image"))
        return Template(
            array=array,
            ox=document["ox"],
            oy=document["oy"],
            name=document["name"],
            url=document["url"],
            owner=document["owner"],
        )

    async def check_name_exists(self, name, **query):
        """
        Check if a template name already exists.
        """
        query["name"] = name
        if await self.collection.find_one(query, {"image": False}):
            return True
        return False

    async def find(self, projection, **query):
        """
        Get a generator returning data from an arbitrary find query.
        """
        async for document in self.collection.find(query, projection):
            yield document

    async def get_templates(self, **query):
        """
        Get a generator returning templates in the database matching the query.
        """
        async for document in self.collection.find(query, {"_id": False}):
            array = self.deserialize(document.pop("image"))
            yield Template(
                array=array,
                ox=document["ox"],
                oy=document["oy"],
                name=document["name"],
                url=document["url"],
                owner=document["owner"],
            )

    async def delete_template(self, **query):
        """
        Delete a template from the database.
        """
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
