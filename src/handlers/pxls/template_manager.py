import pickle
from bson.binary import Binary
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from .progress import Progress
from .template import Template


class TemplateManager:
    """
    An helper used to ease interactions with the templates stored
    in the mongodb databse.
    """

    def __init__(self, mongo_uri: str):
        """
        :param mongo_uri: The mongodb's uri, ie: mongodb://127.0.0.1:27017/
        """
        mongo_client = AsyncIOMotorClient(mongo_uri)
        self.collection = mongo_client.pycharity.templates

    @staticmethod
    def _serialize(array: np.ndarray) -> Binary:
        """Convert a numpy array to a binary blob."""
        return Binary(pickle.dumps(array, protocol=2), subtype=128)

    @staticmethod
    def _deserialize(data: Binary) -> np.ndarray:
        """Retrieve a numpy array from a binary blob."""
        return pickle.loads(data)

    def _doc2template(self, document):
        """
        Convert a document to a template.
        """
        array = self._deserialize(document["image"])
        return Template(
            array=array,
            ox=document["ox"],
            oy=document["oy"],
            name=document["name"],
            canvas_code=document["canvas_code"],
            url=document["url"],
            owner=document["owner"],
            scope=document["scope"],
            progress=Progress(**document["progress"]),
        )

    def _template2doc(self, template: Template):
        """
        Convert a template to a document.
        """
        data = {
            "name": template.name,
            "owner": template.owner,
            "scope": template.scope,
            "canvas_code": template.canvas_code,
            "ox": template.ox,
            "oy": template.oy,
            "url": template.url,
            "image": self._serialize(template.image),
            "progress": template.progress.to_dict(),
        }
        return data

    async def add_template(self, template: Template):
        """
        Add a template to the database.
        """
        data = self._template2doc(template)
        await self.collection.insert_one(data)

    async def update_template(self, template: Template, data=None):
        """
        Update a template from the database.

        :param data: A dictionary of fields to update. If set to None, updates all fields.
        """
        if data is None:
            data = self._template2doc(template)
        await self.collection.update_one(
            {"name": template.name, "canvas_code": template.canvas_code}, {"$set": data}
        )

    async def get_template(self, **query) -> Template:
        """
        Find a template in the database matching the query.
        ex: self.get_template(name='Seon', owner=123456789)
        """
        document = await self.collection.find_one(query)
        if document is None:
            return None
        return self._doc2template(document)

    async def check_name_exists(self, name, **query):
        """
        Check if a template name already exists.
        """
        query["name"] = name
        if await self.collection.find_one(query, {"image": False}):
            return True
        return False

    # pylint: disable = dangerous-default-value
    async def find(self, projection={}, **query):
        """
        Get a generator returning data from an arbitrary find query.
        """
        async for document in self.collection.find(query, projection):
            yield document

    # pylint: disable = dangerous-default-value
    async def find_one(self, projection={}, **query):
        """
        Get the data from an arbitrary find query.
        """
        return await self.collection.find_one(query, projection)

    async def get_templates(self, **query):
        """
        Get a generator returning templates in the database matching the query.
        """
        async for document in self.collection.find(query):
            yield self._doc2template(document)

    async def delete_template(self, **query):
        """
        Delete a template from the database.
        """
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
