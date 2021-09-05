from typing import AsyncGenerator, List, Dict, Any
from handlers.database import DatabaseConnector
from handlers.pxls.stats import StatsRecord


class StatsManager(DatabaseConnector):
    """
    An helper used to ease interactions with the StatsRecord stored
    in the mongodb databse.
    """

    def __init__(self, mongo_uri: str):
        """
        :param mongo_uri: The mongodb's uri, ie: mongodb://127.0.0.1:27017/
        """
        super().__init__(mongo_uri, "stats")

    @staticmethod
    def _record2doc(record: StatsRecord) -> dict:
        """
        Convert a StatsRecord to a document.
        """
        document: Dict[str, Any] = {}
        # pylint: disable = protected-access
        document["stats"] = record._stats
        document["canvas_code"] = record.canvas_code
        document["_id"] = record.time
        return document

    @staticmethod
    def _doc2record(document: dict) -> StatsRecord:
        """
        Convert a document to a StatsRecord.
        """
        return StatsRecord(
            time=document["_id"],
            stats_dict=document["stats"],
            canvas_code=document["canvas_code"],
        )

    async def add_record(self, record: StatsRecord):
        """
        Add a StatsRecord to the database.
        """
        data = self._record2doc(record)
        await self.collection.insert_one(data)

    async def get_history(
        self,
        usernames: List[str],
        canvas_code: str,
    ) -> AsyncGenerator[StatsRecord, None]:
        """
        Get a user's stats history, sorted by increasing time.
        """
        user_query = {f"stats.{username}": {"$exists": True} for username in usernames}
        user_projection = {f"stats.{username}": True for username in usernames}
        async for document in self.collection.find(
            {"canvas_code": canvas_code, **user_query},
            {"time": True, "canvas_code": True, **user_projection},
        ).sort("time"):
            yield self._doc2record(document)
