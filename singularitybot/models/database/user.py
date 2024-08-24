import datetime
import disnake

from typing import List, Union, Optional

from typing import TYPE_CHECKING

from math import sqrt

# It's for typehint
if TYPE_CHECKING:
    from singularitybot.models.database.maindatabase import Database

from singularitybot.models.gameobjects.character import Character, character_from_dict
from singularitybot.models.gameobjects.items import Item, item_from_dict

USRXPTOLEVEL = 100
LVLSCALING = 0.09

class User:
    """| Class used as an interface to data ,Any change made to the class is also made to the data"""

    def __init__(self, data: dict, database: "Database"):
        """Class constructor

        Args:
            data (dict): User dict (see maindatabase file)
            database (_type_): An Instance of Databse (for Updates)
        """
        # Initialization variables
        self.data: dict = data
        self.database: "Database" = database
        # Inerant variables
        self.id: str = data["_id"]
        self.main_characters: List[Character] = [
            character_from_dict(s) for s in data["main_characters"]
        ]
        self.galaxy_id: Optional[str] = data["galaxy_id"]
        self.shop_id : Optional[str] = data["shop_id"]
        self.character_storage_1: List[Character] = [
            character_from_dict(s) for s in data["character_storage_1"]
        ]
        self.character_storage_2: List[Character] = [
            character_from_dict(s) for s in data["character_storage_2"]
        ]
        self.character_storage_3: List[Character] = [
            character_from_dict(s) for s in data["character_storage_3"]
        ]
        self.character_storage_4: List[Character] = [
            character_from_dict(s) for s in data["character_storage_4"]
        ]
        self.pcharacter_storage_1: List[Character] = [
            character_from_dict(s) for s in data["pcharacter_storage_1"]
        ]
        self.pcharacter_storage_2: List[Character] = [
            character_from_dict(s) for s in data["pcharacter_storage_2"]
        ]
        self.pcharacter_storage_3: List[Character] = [
            character_from_dict(s) for s in data["pcharacter_storage_3"]
        ]
        self.pcharacter_storage_4: List[Character] = [
            character_from_dict(s) for s in data["pcharacter_storage_4"]
        ]
        self.character_storage_list: List[List[Character]] = [self.character_storage_1, self.character_storage_2, self.character_storage_3, self.character_storage_4]
        self.pcharacter_storage_list: List[List[Character]] = [self.pcharacter_storage_1, self.pcharacter_storage_2, self.pcharacter_storage_3, self.pcharacter_storage_4]
        self.items: List[Item] = [item_from_dict(s) for s in data["items"]]
        self.achievements: List[int] = data["achievements"]
        self.galaxies_invites: List[int] = data["galaxies_invites"]
        self.custom_character: int = data["custom_character"]
        self.fragments: int = data["fragments"]
        self.super_fragements : int = data["super_fragements"]
        self.xp = data["xp"]
        self.level: int = min(USRXPTOLEVEL,int(LVLSCALING*sqrt(self.xp)))  # cap xp to 100
        self.energy: int = data["energy"]
        self.total_energy: int = int(10 + (self.level//5))
        self.pity: int = data["pity"]
        self.job: dict = data["job"]
        self.prestige: int = data["prestige"]
        self.global_elo: int = data["global_elo"]
        self.missions_level: int = data["missions_level"]
        self.tower_level: int = data["tower_level"]
        self.map_position: List[int] = data["map_position"]
        self.profile_image: str = data["profile_image"]
        self.join_date: datetime.datetime = data["join_date"]
        self.last_full_energy:datetime.datetime = data["last_full_energy"]
        self.last_missions: datetime.datetime = data["last_missions"]
        self.last_wormhole: datetime.datetime = data["last_wormhole"]
        self.last_adventure: datetime.datetime = data["last_adventure"]
        self.last_job: datetime.datetime = data["last_job"]
        self.last_vote: datetime.datetime = data["last_vote"]
        self.last_advert: datetime.datetime = data["last_advert"]
        self.donor_status: datetime.datetime = data["donor_status"]
        self.early_supporter: bool = data["early_supporter"]
        self.discord: Optional[Union[disnake.User, disnake.Member]] = None
        self.message: Optional[disnake.Message] = None
        self.is_human = True  # used in fight to determine who is human

    async def update(self) -> None:
        """Update the user info in the database"""
        await self.database.update_user(self.to_dict())

    def is_donator(self):
        status = self.early_supporter
        # regular donor status
        status |= self.donor_status >= (
            datetime.datetime.now() + datetime.timedelta(hours=2)
        )
        # answer
        return status
    
    def add_to_available_storage(self, character: "Character", skip_main:bool=False):
        if len(self.main_characters) < 3 and not skip_main:
            self.main_characters.append(character)
            return "Main Characters Storage"
        for i,storage in enumerate(self.character_storage_list):
            if len(storage) < 25:
                storage.append(character)
                return f"Storage n°{i}"
        for i,storage in enumerate(self.pcharacter_storage_list):
            if len(storage) < 25:
                storage.append(character)
                return f"Premium Storage n°{i}"
        return False
    def to_dict(self) -> dict:
        """Convert Class to storable data

        Returns:
            dict: character
        """
        self.data["main_characters"] = [s.to_dict() for s in self.main_characters]
        self.data["galaxy_id"] = self.galaxy_id
        self.data["shop_id"] = self.shop_id
        self.data["character_storage_1"] = [s.to_dict() for s in self.character_storage_1]
        self.data["character_storage_2"] = [s.to_dict() for s in self.character_storage_2]
        self.data["character_storage_3"] = [s.to_dict() for s in self.character_storage_3]
        self.data["character_storage_4"] = [s.to_dict() for s in self.character_storage_4]
        self.data["pcharacter_storage_1"] = [s.to_dict() for s in self.pcharacter_storage_1]
        self.data["pcharacter_storage_2"] = [s.to_dict() for s in self.pcharacter_storage_2]
        self.data["pcharacter_storage_3"] = [s.to_dict() for s in self.pcharacter_storage_3]
        self.data["pcharacter_storage_4"] = [s.to_dict() for s in self.pcharacter_storage_4]
        self.data["items"] = [s.to_dict() for s in self.items]
        self.data["achievements"] = self.achievements
        self.data["galaxies_invites"] = self.galaxies_invites
        self.data["custom_character"] = self.custom_character
        self.data["energy"] = self.energy
        self.data["fragments"] = self.fragments
        self.data["super_fragements"] = self.super_fragements
        self.data["pity"] = self.pity
        self.data["xp"] = self.xp
        self.data["job"] = self.job
        self.data["prestige"] = self.prestige
        self.data["global_elo"] = self.global_elo
        self.data["missions_level"] = self.missions_level
        self.data["tower_level"] = self.tower_level
        self.data["map_position"] = self.map_position
        self.data["profile_image"] = self.profile_image
        self.data["join_date"] = self.join_date
        self.data["last_full_energy"] = self.last_full_energy
        self.data["last_missions"] = self.last_missions
        self.data["last_adventure"] = self.last_adventure
        self.data["last_vote"] = self.last_vote
        self.data["last_job"] = self.last_job
        self.data["last_advert"] = self.last_advert
        self.data["last_wormhole"] = self.last_wormhole
        self.data["donor_status"] = self.donor_status
        self.data["early_supporter"] = self.early_supporter
        return self.data


def create_user(user_id: str):
    data = {
        "_id": user_id,
        "galaxy_id": None,
        "shop_id":None,
        "main_characters": [],
        "character_storage_1": [],
        "character_storage_2": [],
        "character_storage_3": [],
        "character_storage_4": [],
        "pcharacter_storage_1": [],
        "pcharacter_storage_2": [],
        "pcharacter_storage_3": [],
        "pcharacter_storage_4": [],
        "items": [],
        "achievements": [],
        "galaxies_invites": [],
        "custom_character": None,
        "fragments": 0,
        "super_fragements":0,
        "pity":0,
        "xp": 0,
        "energy": 10,
        "job": None,
        "prestige": 0,
        "global_elo": 0,
        "missions_level": 0,
        "tower_level": 0,
        "map_position": [0, 0],
        "profile_image": "https://i.pinimg.com/originals/77/ba/e4/77bae4f9d1c02f732e9271976539ed48.gif",
        "join_date": (datetime.datetime.now() + datetime.timedelta(hours=2)),
        "last_full_energy": (datetime.datetime.now() + datetime.timedelta(hours=2)),
        "last_missions": datetime.datetime.min,
        "last_adventure": datetime.datetime.min,
        "last_vote": datetime.datetime.min,
        "last_job": datetime.datetime.min,
        "last_advert": datetime.datetime.min,
        "last_wormhole": datetime.datetime.min,
        "donor_status": datetime.datetime.min,
        "early_supporter": False,
    }
    return data
