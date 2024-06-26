import datetime
from typing import List

class War:
    def __init__(self, id: int, galaxy1_id: int, galaxy2_id: int, start_time: datetime.datetime, end_time: datetime.datetime, status: str, galaxy1_wins: int = 0, galaxy2_wins: int = 0):
        self.id = id
        self.galaxy1_id = galaxy1_id
        self.galaxy2_id = galaxy2_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.galaxy1_wins = galaxy1_wins
        self.galaxy2_wins = galaxy2_wins

    async def update(self, database):
        await database.update_war(self)
