import datetime
import disnake

from typing import List, Union, Optional

from typing import TYPE_CHECKING

# It's for typehint
if TYPE_CHECKING:
    from singularitybot.models.database.maindatabase import Database


class Guild:
    def __init__(self, data: dict, database: "Database"):
        self.data = data
        self.database = database

        self.lang: str = data["lang"]
        self.donor_status: datetime.datetime = data["donor_status"]
        self.join_voice: bool = data["join_voice"]
        self.allowed_channels: list = data["allowed_channels"]

    async def update(self):
        await self.database.update_guild(self.to_dict())

    def to_dict(self) -> dict:
        self.data["lang"] = self.lang
        self.data["donor_status"] = self.donor_status
        self.data["allowed_channels"] = self.allowed_channels
        self.data["join_voice"] = self.join_voice
        return self.data


def create_guild(id: str):
    return {
        "_id": id,
        "lang": "en_US",
        "join_voice": False,
        "allowed_channels": [],
        "donor_status": datetime.datetime.min,
    }
