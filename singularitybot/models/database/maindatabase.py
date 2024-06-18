import motor.motor_asyncio
import asyncio
import os
import disnake
import json
import random
import datetime

from typing import Union, List, Dict


from singularitybot.models.database.user import User, create_user
from singularitybot.models.database.guild import Guild, create_guild
from singularitybot.models.database.cache import Cache
from singularitybot.models.gameobjects.shop import Shop, create_shop
from singularitybot.models.gameobjects.items import Item
from singularitybot.models.gameobjects.galaxy import Galaxy, create_galaxy


MONGO_URL = os.environ["MONGO_URL"]


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        """Main Database instance of the redis cache included

        Args:
            loop (asyncio.AbstractEventLoop): the current asyncio loop running
        """
        # Initialization of the cache
        self.cache = Cache()
        # Define the main database objects ( client , database , collections )
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        self.db: motor.motor_asyncio.AsyncIOMotorDatabase = self.client[
            "singularity_db"
        ]
        self.users: motor.motor_asyncio.AsyncIOMotorCollection = self.db["users"]
        self.servers: motor.motor_asyncio.AsyncIOMotorCollection = self.db["servers"]
        self.logs: motor.motor_asyncio.AsyncIOMotorCollection = self.db["logs"]
        self.galaxies: motor.motor_asyncio.AsyncIOMotorCollection = self.db["galaxies"]
        self.ban: motor.motor_asyncio.AsyncIOMotorCollection = self.db["bans"]

    async def add_user(self, user_id: Union[str, int]):
        """Add a user to the database
        Args:
            user_id (int): Unique discord identifier
        """
        # set integers as a string
        if isinstance(user_id, int):
            user_id = str(user_id)
        document = create_user(user_id)
        await self.cache.this_data(document)
        await self.users.insert_one(document)

    async def add_guild(self, guild_id: Union[str, int]):
        """add a guild to the database

        Args:
            guild_id (Union[str, int]): Unique discord identifier
        """
        # set integers as a string
        if isinstance(guild_id, int):
            guild_id = str(guild_id)
        document = create_guild(guild_id)
        await self.servers.insert_one(document)

    async def get_user_info(self, user_id: Union[str, int]) -> User:
        """Retrieve the User information from the database

        Args:
            id (Union[str, int]): The ID of the user info

        Returns:
            User: the user class
        """
        # set integers as a string
        if isinstance(user_id, int):
            user_id = str(user_id)
        # cache management
        if await self.cache.is_cached(user_id):
            document = await self.cache.get_data(user_id)
            return User(document, self)
        document = await self.users.find_one({"_id": user_id})
        # cache the data
        await self.cache.this_data(document)
        return User(document, self)

    async def get_guild_info(self, guild_id: Union[str, int]) -> Guild:
        """Retrieve the guild information from the database

        Args:
            id (Union[str, int]): The ID of the guilg info

        Returns:
            dict: the information
        """
        # set integers as a string
        if isinstance(guild_id, int):
            guild_id = str(guild_id)
        # cache management
        if await self.cache.is_cached(guild_id):
            document = await self.cache.get_data(guild_id)
            return Guild(document, self)
        document = await self.servers.find_one({"_id": guild_id})
        # cache the data
        await self.cache.this_data(document)
        return Guild(document, self)

    async def update_user(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        _id = document["_id"]
        await self.users.replace_one({"_id": _id}, document)
        if await self.cache.is_cached(_id):
            await self.cache.this_data(document)

    async def update_guild(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        _id = document["_id"]
        await self.servers.replace_one({"_id": _id}, document)
        if await self.cache.is_cached(_id):
            await self.cache.this_data(document)

    async def user_in_database(self, user_id: Union[str, int]) -> bool:
        """Check if the user is registered

        Args:
            user_id (Union[str, int]): the unique discord id

        Returns:
            bool: the answer
        """
        # set integers as a string
        if isinstance(user_id, int):
            user_id = str(user_id)
        # if data is cached then it mean the user is registered
        if await self.cache.is_cached(user_id):
            return True
        # Else we check if we can get any data
        return not (await self.users.find_one({"_id": user_id}) == None)

    async def guild_in_database(self, guild_id: Union[str, int]) -> bool:
        """Check if the user is registered

        Args:
            user_id (Union[str, int]): the unique discord id

        Returns:
            bool: the answer
        """
        # set integers as a string
        if isinstance(guild_id, int):
            guild_id = str(guild_id)
        # if data is cached then it mean the user is registered
        if await self.cache.is_cached(guild_id):
            return True
        # Else we check if we can get any data
        return not (await self.servers.find_one({"_id": guild_id}) == None)

    async def get_interaction_lang(
        self, Interaction: disnake.ApplicationCommandInteraction
    ) -> Dict[str, Dict[str, str]]:
        """Get the localization file from the database

        Args:
            Interaction (disnake.ApplicationCommandInteraction): Interaction

        Returns:
            dict: the localization file as json
        """
        id = Interaction.guild.id
        # if the guild is not registered the we register it
        if not await self.guild_in_database(id):
            await self.add_guild(id)
        guild = await self.get_guild_info(id)
        with open(f"stfubot/lang/{guild.lang}.json", "r", encoding="utf8") as item:
            translation = json.load(item)
        return translation

    async def add_shop(self, name: str, description: str, user_id: str) -> str:
        """add a shop into the database

        Args:
            name (str): name of the shop
            description (str):

        Returns:
            str: id of the shop
        """
        document = create_shop(name, description, user_id)
        await self.cache.this_data(document)
        await self.shops.insert_one(document)
        return document["_id"]

    async def get_shop_info(self, shop_id: str) -> Shop:
        """Retrieve the Shop information from the database

        Args:
            shop_id str: The ID of the shop info

        Returns:
            Shop: the Shop class
        """

        # cache management
        if await self.cache.is_cached(shop_id):
            document = await self.cache.get_data(shop_id)
            return Shop(document, self)
        document = await self.shops.find_one({"_id": shop_id})
        # cache the data
        await self.cache.this_data(document)
        return Shop(document, self)

    async def update_shop(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        _id = document["_id"]
        await self.shops.replace_one({"_id": _id}, document)
        if await self.cache.is_cached(_id):
            await self.cache.this_data(document)

    async def find_suitable_shop(
        self, item_to_find: Item, user_shop_id: str
    ) -> Tuple[Shop, int]:
        """This fonction finds a shop with the right item

        Args:
            item_to_find (Item): item to find
            user_shop_id (str): user shop id to exclude

        Returns:
            Tuple[Shop, int]: the suitable shop and the item index
        """
        shops: List[Shop] = []
        docs = self.shops.find({"items": {"id": item_to_find.id}})
        docs = await docs.to_list(length=100)
        for doc in docs:
            if doc["_id"] != user_shop_id:
                shops.append(Shop(doc, self))
        # If no shops as the item
        if len(shops) == 0:
            return None, 0
        # we take a random shop to have a healthier economy
        suitable_shop = random.choice(shops)
        # get the index of the item to find
        index = [i.id for i in suitable_shop.items].index(item_to_find.id)
        return (suitable_shop, index)

    async def add_galaxy(self, user_id: str, name: str, motd: str, motto: str) -> str:
        """add a galaxy to the database

        Args:
            user_id (str): the id of the user who created the galaxy
            name (str): the name of the galaxy
            motd (str): the motd of the galaxy
            motto (str): the motto of the galaxy

        Returns:
            str: the id of the galaxy
        """
        document = create_galaxy(user_id, name, motd, motto)
        await self.cache.this_data(document)
        await self.galaxies.insert_one(document)
        return document["_id"]

    async def get_galaxy_info(self, galaxy_id: str) -> Galaxy:
        """Retrieve the galaxy information from the database

        Args:
            galaxy_id str: The ID of the galaxy info

        Returns:
            galaxy: the galaxy class
        """

        # cache management
        if await self.cache.is_cached(galaxy_id):
            document = await self.cache.get_data(galaxy_id)
            return Galaxy(document, self)
        document = await self.galaxies.find_one({"_id": galaxy_id})
        # cache the data
        await self.cache.this_data(document)
        return Galaxy(document, self)

    async def update_galaxy(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        _id = document["_id"]
        await self.galaxies.replace_one({"_id": _id}, document)
        if await self.cache.is_cached(_id):
            await self.cache.this_data(document)

    async def close(self):
        await self.client.close()
        await self.cache.close()

    async def add_log(
        self,
        date: datetime.datetime,
        command_name: str,
        error_name: str,
        traceback: str,
    ) -> None:
        """add an error log to the database

        Args:
            date (datetime.datetime): date of the error
            command_name (str): command that triggered the error
            error_name (str): the error name
            traceback (str): the error traceback
        """

        log = {
            "date": date,
            "command": command_name,
            "error_name": error_name,
            "traceback": traceback,
        }
        await self.logs.insert_one(log)


async def add_field(
    collection: motor.motor_asyncio.AsyncIOMotorCollection,
    fields: List[str],
    default_values: List,
):
    """
    DO NOT USE IN CODE ITS A UTIL FONCTION
    """
    for value, field in zip(default_values, fields):
        result = await collection.update_many({}, {"$set": {field: value}})
        print("matched %d, modified %d" % (result.matched_count, result.modified_count))


if __name__ == "__main__":
    
    async def main():
        loop = asyncio.get_event_loop()
        db = Database(loop)
        fields = [
            "last_full_energy",
        ]
        values = [datetime.datetime.min]
        await add_field(db.users, fields, values)
    
    loop = asyncio.get_event_loop()
    db = Database(loop)
    loop.run_until_complete(main())
