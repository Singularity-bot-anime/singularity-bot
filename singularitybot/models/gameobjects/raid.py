import datetime
from typing import List

class Raid:
    def __init__(self, id: int, galaxy_id: int, target_id: int, members: List[int], start_time: datetime.datetime, end_time: datetime.datetime, status: str):
        self.id = id
        self.galaxy_id = galaxy_id
        self.target_id = target_id
        self.members = members
        self.start_time = start_time
        self.end_time = end_time
        self.status = status

    async def update(self, database):
        await database.update_raid(self)
