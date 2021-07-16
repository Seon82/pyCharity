from typing import Optional
from datetime import datetime


class StatsRecord:
    """
    An object used to contain the stats
    info for all users at a given time.
    """

    def __init__(self, time: datetime, stats_dict: dict, canvas_code: str):
        self.time = time
        self.canvas_code = canvas_code
        self._stats = stats_dict

    def get(self, username: str) -> Optional[dict]:
        """
        Get the stats for a user.
        """
        return self._stats.get(username)

    @classmethod
    def from_json(cls, json: dict, canvas_code: str):
        """
        Generate a StatsRecord object from the data
        at pxls.space/stats/stats.json.
        """
        date_str = json["generatedAt"].split(" (")[0]
        time = datetime.strptime(date_str, "%Y/%m/%d - %H:%M:%S")
        stats_dict = dict()
        for stats in json["toplist"]["canvas"]:
            stats_dict[stats["username"]] = {
                "pixels": stats["pixels"],
                "place": stats["place"],
            }
        return cls(time, stats_dict, canvas_code)
