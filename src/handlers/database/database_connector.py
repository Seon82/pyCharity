import pickle
from typing import Iterator
from bson.binary import Binary
from motor.motor_asyncio import AsyncIOMotorClient


class DatabaseConnector:
    """
    A helper used to easily interact with
    a mongodb database.
    """

    def __init__(self, mongo_uri: str, collection_name: str):
        """
        :param mongo_uri: The mongodb's uri, ie: mongodb://127.0.0.1:27017/
        :param collection_name: THe collection this database connector should interact with.
        """
        mongo_client = AsyncIOMotorClient(mongo_uri)
        self.collection = mongo_client.pycharity[collection_name]

    @staticmethod
    def _serialize(data) -> Binary:
        """Convert a python object to a binary blob."""
        return Binary(pickle.dumps(data, protocol=2), subtype=128)

    @staticmethod
    def _deserialize(data: Binary):
        """Retrieve a python object from a binary blob."""
        return pickle.loads(data)

    # pylint: disable = dangerous-default-value
    async def find(self, projection={}, **query) -> Iterator[dict]:
        """
        Get a generator returning data from an arbitrary find query.
        """
        async for document in self.collection.find(query, projection):
            yield document

    # pylint: disable = dangerous-default-value
    async def find_one(self, projection={}, **query) -> dict:
        """
        Get the data from an arbitrary find query.
        """
        return await self.collection.find_one(query, projection)
