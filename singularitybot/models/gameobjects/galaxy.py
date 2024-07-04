import uuid
import datetime
from enum import Enum


from typing import List, TYPE_CHECKING

from singularitybot.globals.variables import GANGURL

if TYPE_CHECKING:
    from singularitybot.models.database.maindatabase import Database
from singularitybot.models.gameobjects.character import Character, character_from_dict
from singularitybot.models.gameobjects.items import Item, item_from_dict


class GalaxyRank(int, Enum):
    BOSS = 0
    STAR = 1
    STARDUST = 2


class Galaxy:
    def __init__(self, data: dict, database: "Database"):
        self.data = data
        self.database = database
        self.id: str = data["_id"]
        self.name: str = data["name"]
        self.motd: str = data["motd"]
        self.motto: str = data["motto"]
        self.image_url: str = data["image_url"]
        self.users: List[str] = data["users"]
        self.ranks: dict = data["ranks"]
        self.vault: int = data["vault"]
        self.characters: List[Character] = [character_from_dict(s) for s in data["characters"]]
        self.items: List[Item] = [item_from_dict(s) for s in data["items"]]
        self.raid_level: int = data["raid_level"]
        self.war_elo: int = data["war_elo"]
        self.war_attacks:List[str] = list(data["war_attacks"])
        self.raid_attacks:List[str] = list(data["raid_attacks"])
        self.damage_to_current_war: int = data["damage_to_current_war"]
        self.damage_to_current_raid: int = data["damage_to_current_raid"]
        self.end_of_raid: datetime.datetime = data["end_of_raid"]
        self.end_of_war: datetime.datetime = data["end_of_war"]
        self.last_raid: datetime.datetime = data["last_raid"]
        self.last_war: datetime.datetime = data["last_war"]

    def to_dict(self) -> dict:
        """update the data and returns it

        Returns:
            dict: the info of the Galaxy
        """
        self.data["motd"] = self.motd
        self.data["motto"] = self.motto
        self.data["image_url"] = self.image_url
        self.data["users"] = self.users
        self.data["ranks"] = self.ranks
        self.data["vault"] = self.vault
        self.data["characters"] = [s.to_dict() for s in self.characters]
        self.data["items"] = [s.to_dict() for s in self.items]
        self.data["raid_level"] = self.raid_level
        self.data["war_elo"] = self.war_elo
        self.data["war_attacks"] = self.war_attacks
        self.data["raid_attacks"] = self.raid_attacks
        self.data["damage_to_current_war"] = self.damage_to_current_war
        self.data["damage_to_current_raid"] = self.damage_to_current_raid
        self.data["end_of_raid"] = self.end_of_raid
        self.data["end_of_war"] = self.end_of_war
        self.data["last_raid"] = self.last_raid
        self.data["last_war"] = self.last_war
        return self.data

    async def update(self) -> None:
        await self.database.update_galaxy(self.to_dict())


def create_galaxy(user_id: str, name: str, motd: str, motto: str) -> dict:
    data = {
        "_id": str(uuid.uuid4()),
        "name": name,
        "motd": motd,
        "image_url": GANGURL,
        "motto": motto,
        "users": [user_id],
        "ranks": {user_id: 0},
        "vault": 0,
        "characters": [],
        "items": [],
        "raid_level": 1,
        "war_elo": 0,
        "war_attacks":[],
        "raid_attacks":[],
        "damage_to_current_war": 0,
        "damage_to_current_raid": 0,
        "end_of_raid": datetime.datetime.min,
        "end_of_war": datetime.datetime.min,
        "last_raid": datetime.datetime.min,
        "last_war": datetime.datetime.min,
    }
    return data
