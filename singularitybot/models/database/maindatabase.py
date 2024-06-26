import asyncio
import os
import pickle
import random
import datetime
import disnake
import aiohttp
import io

from PIL import Image, ImageDraw,ImageFont

from typing import Union, List, Dict, Callable, Any
from redis.asyncio import Redis, ConnectionPool
from singularitybot.models.database.user import User, create_user
from singularitybot.models.database.guild import Guild, create_guild
from singularitybot.models.gameobjects.shop import Shop, create_shop
from singularitybot.models.gameobjects.items import Item
from singularitybot.models.gameobjects.galaxy import Galaxy, create_galaxy
from singularitybot.models.gameobjects.war import War
from singularitybot.models.gameobjects.raid import Raid


# Run localy
import sys
if (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
    print("LOCAL URL LOAD")
    from dotenv import load_dotenv
    load_dotenv()


REDIS_URL = os.environ["REDIS_URL"]

class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        """Main Database instance with Redis pub/sub included

        Args:
            loop (asyncio.AbstractEventLoop): the current asyncio loop running
        """
        self.redis_pool = ConnectionPool.from_url(REDIS_URL, decode_responses=False)
        self.loop = loop

    async def get_redis_connection(self) -> Redis:
        """Get a Redis connection from the connection pool."""
        return Redis(connection_pool=self.redis_pool)

    async def publish(self, channel: str, message: dict) -> None:
        """Publish a message to a Redis channel"""
        async with await self.get_redis_connection() as conn:
            await conn.publish(channel, pickle.dumps(message))

    async def subscribe(self, channel: str, message_handler: Callable[[str, Any], None]) -> None:
        """Subscribe to a Redis channel"""
        async with await self.get_redis_connection() as conn:
            pubsub = conn.pubsub()
            await pubsub.subscribe(channel)

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = pickle.loads(message['data'])
                    message_handler(channel, data)
    
    async def create_fight(self,request):
        await self.publish("match_queue",request)

    async def add_user(self, user_id: Union[str, int]):
        """Add a user to the database
        Args:
            user_id (int): Unique discord identifier
        """
        async with await self.get_redis_connection() as conn:
            if isinstance(user_id, int):
                user_id = str(user_id)
            document = create_user(user_id)
            await conn.hset("users", user_id, pickle.dumps(document))

    async def add_guild(self, guild_id: Union[str, int]):
        """Add a guild to the database

        Args:
            guild_id (Union[str, int]): Unique discord identifier
        """
        async with await self.get_redis_connection() as conn:
            if isinstance(guild_id, int):
                guild_id = str(guild_id)
            document = create_guild(guild_id)
            await conn.hset("guilds", guild_id, pickle.dumps(document))

    async def get_user_info(self, user_id: Union[str, int]) -> User:
        """Retrieve the User information from the database

        Args:
            id (Union[str, int]): The ID of the user info

        Returns:
            User: the user class
        """
        async with await self.get_redis_connection() as conn:
            if isinstance(user_id, int):
                user_id = str(user_id)
            document = await conn.hget("users", user_id)
            document = pickle.loads(document) if document else None
            return User(document, self)

    async def get_guild_info(self, guild_id: Union[str, int]) -> Guild:
        """Retrieve the guild information from the database

        Args:
            id (Union[str, int]): The ID of the guild info

        Returns:
            dict: the information
        """
        async with await self.get_redis_connection() as conn:
            if isinstance(guild_id, int):
                guild_id = str(guild_id)
            document = await conn.hget("guilds", guild_id)
            document = pickle.loads(document) if document else None
            return Guild(document, self)

    async def update_user(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        async with await self.get_redis_connection() as conn:
            _id = document["_id"]
            await conn.hset("users", _id, pickle.dumps(document))

    async def update_guild(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        async with await self.get_redis_connection() as conn:
            _id = document["_id"]
            await conn.hset("guilds", _id, pickle.dumps(document))

    async def user_in_database(self, user_id: Union[str, int]) -> bool:
        """Check if the user is registered

        Args:
            user_id (Union[str, int]): the unique discord id

        Returns:
            bool: the answer
        """
        async with await self.get_redis_connection() as conn:
            if isinstance(user_id, int):
                user_id = str(user_id)
            return await conn.hexists("users", user_id)

    async def guild_in_database(self, guild_id: Union[str, int]) -> bool:
        """Check if the guild is registered

        Args:
            guild_id (Union[str, int]): the unique discord id

        Returns:
            bool: the answer
        """
        async with await self.get_redis_connection() as conn:
            if isinstance(guild_id, int):
                guild_id = str(guild_id)
            return await conn.hexists("guilds", guild_id)

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
        if not await self.guild_in_database(id):
            await self.add_guild(id)
        guild = await self.get_guild_info(id)
        with open(f"stfubot/lang/{guild.lang}.json", "r", encoding="utf8") as item:
            translation = json.load(item)
        return translation

    async def add_shop(self, name: str, description: str, user_id: str) -> str:
        """Add a shop into the database

        Args:
            name (str): name of the shop
            description (str): description of the shop

        Returns:
            str: id of the shop
        """
        async with await self.get_redis_connection() as conn:
            document = create_shop(name, description, user_id)
            await conn.hset("shops", document["_id"], pickle.dumps(document))
            return document["_id"]

    async def get_shop_info(self, shop_id: str) -> Shop:
        """Retrieve the Shop information from the database

        Args:
            shop_id str: The ID of the shop info

        Returns:
            Shop: the Shop class
        """
        async with await self.get_redis_connection() as conn:
            document = await conn.hget("shops", shop_id)
            document = pickle.loads(document) if document else None
            return Shop(document, self)

    async def update_shop(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        async with await self.get_redis_connection() as conn:
            _id = document["_id"]
            await conn.hset("shops", _id, pickle.dumps(document))

    async def find_suitable_shop(
        self, item_to_find: Item, user_shop_id: str
    ) -> tuple[Shop, int]:
        """This function finds a shop with the right item

        Args:
            item_to_find (Item): item to find
            user_shop_id (str): user shop id to exclude

        Returns:
            Tuple[Shop, int]: the suitable shop and the item index
        """
        async with await self.get_redis_connection() as conn:
            shops = []
            all_shops = await conn.hgetall("shops")
            for doc in all_shops.values():
                doc = pickle.loads(doc)
                if doc["_id"] != user_shop_id and any(item["id"] == item_to_find.id for item in doc["items"]):
                    shops.append(Shop(doc, self))
            if len(shops) == 0:
                return None, 0
            suitable_shop = random.choice(shops)
            index = next(i for i, item in enumerate(suitable_shop.items) if item.id == item_to_find.id)
            return suitable_shop, index

    async def add_galaxy(self, user_id: str, name: str, motd: str, motto: str) -> str:
        """Add a galaxy to the database

        Args:
            user_id (str): the id of the user who created the galaxy
            name (str): the name of the galaxy
            motd (str): the motd of the galaxy
            motto (str): the motto of the galaxy

        Returns:
            str: the id of the galaxy
        """
        async with await self.get_redis_connection() as conn:
            document = create_galaxy(user_id, name, motd, motto)
            await conn.hset("galaxies", document["_id"], pickle.dumps(document))
            return document["_id"]

    async def get_galaxy_info(self, galaxy_id: str) -> Galaxy:
        """Retrieve the galaxy information from the database

        Args:
            galaxy_id str: The ID of the galaxy info

        Returns:
            galaxy: the galaxy class
        """
        async with await self.get_redis_connection() as conn:
            document = await conn.hget("galaxies", galaxy_id)
            document = pickle.loads(document) if document else None
            return Galaxy(document, self)

    async def update_galaxy(self, document: dict) -> None:
        """Update the document in the database

        Args:
            document (dict): The New document
        """
        async with await self.get_redis_connection() as conn:
            _id = document["_id"]
            await conn.hset("galaxies", _id, pickle.dumps(document))

    async def close(self):
        pool = await self.get_redis_connection()
        await pool.close()

    async def add_log(
        self,
        date: datetime.datetime,
        command_name: str,
        error_name: str,
        traceback: str,
    ) -> None:
        """Add an error log to the database

        Args:
            date (datetime.datetime): date of the error
            command_name (str): command that triggered the error
            error_name (str): the error name
            traceback (str): the error traceback
        """
        async with await self.get_redis_connection() as conn:
            log = {
                "date": date,
                "command": command_name,
                "error_name": error_name,
                "traceback": traceback,
            }
            await conn.hset("logs", str(date), pickle.dumps(log))
    async def cache_image(self, key: str, image_data: bytes):
        async with await self.get_redis_connection() as conn:
            await conn.set(key, image_data)

    async def get_cached_image(self, key: str) -> bytes:
        async with await self.get_redis_connection() as conn:
            return await conn.get(key)

    async def get_character_image(self, character_id: int) -> Image:
        key = f"character_image:{character_id}"
        cached_image = await self.get_cached_image(key)
        if cached_image:
            return Image.open(io.BytesIO(cached_image))
        else:
            url = f"https://media.singularityapp.online/images/cards/{character_id}.png"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        await self.cache_image(key, image_data)
                        return Image.open(io.BytesIO(image_data))
                    else:
                        raise ValueError("Failed to fetch image")
    async def add_war(self, war: War):
        async with await self.get_redis_connection() as conn:
            await conn.hset("wars", str(war.id), pickle.dumps(war))

    async def get_active_wars(self) -> List[War]:
        async with await self.get_redis_connection() as conn:
            all_wars = await conn.hgetall("wars")
            active_wars = []
            for war_data in all_wars.values():
                war = pickle.loads(war_data)
                if war.status == "ongoing":
                    active_wars.append(war)
            return active_wars

    async def get_last_war(self) -> War:
        async with await self.get_redis_connection() as conn:
            all_wars = await conn.hgetall("wars")
            if not all_wars:
                return None
            last_war_data = max(all_wars.values(), key=lambda x: pickle.loads(x).end_time)
            return pickle.loads(last_war_data)

    async def add_raid(self, raid: Raid):
        async with await self.get_redis_connection() as conn:
            await conn.hset("raids", str(raid.id), pickle.dumps(raid))

    async def get_active_raids(self) -> List[Raid]:
        async with await self.get_redis_connection() as conn:
            all_raids = await conn.hgetall("raids")
            active_raids = []
            for raid_data in all_raids.values():
                raid = pickle.loads(raid_data)
                if raid.status == "ongoing":
                    active_raids.append(raid)
            return active_raids

    async def get_last_raid(self) -> Raid:
        async with await self.get_redis_connection() as conn:
            all_raids = await conn.hgetall("raids")
            if not all_raids:
                return None
            last_raid_data = max(all_raids.values(), key=lambda x: pickle.loads(x).end_time)
            return pickle.loads(last_raid_data)

    async def update_war(self, war: War):
        async with await self.get_redis_connection() as conn:
            await conn.hset("wars", str(war.id), pickle.dumps(war))

    async def update_raid(self, raid: Raid):
        async with await self.get_redis_connection() as conn:
            await conn.hset("raids", str(raid.id), pickle.dumps(raid))
async def add_field(
    pool: ConnectionPool,
    collection: str,
    fields: List[str],
    default_values: List,
):
    """
    DO NOT USE IN CODE ITS A UTIL FUNCTION
    """
    async with Redis(connection_pool=pool) as conn:
        all_docs = await conn.hgetall(collection)
        for key, doc in all_docs.items():
            doc = pickle.loads(doc)
            for field, value in zip(fields, default_values):
                doc[field] = value
            await conn.hset(collection, key, pickle.dumps(doc))
            print(f"Updated {key}")

if __name__ == "__main__":
    
    async def main():
        loop = asyncio.get_event_loop()
        db = Database(loop)
        fields = [
            "shop_id",
        ]
        values = [None]
        await add_field(db.redis_pool, "users", fields, values)
    
    loop = asyncio.get_event_loop()
    db = Database(loop)
    loop.run_until_complete(main())
