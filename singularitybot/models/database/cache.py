import os
import pickle
from typing import Callable, Any
from redis.asyncio import Redis, ConnectionPool


REDIS_URL = os.environ["REDIS_URL"]


class Cache:
    """Connection to the redis database"""

    def __init__(self):
        self.redis_pool = ConnectionPool.from_url(url=REDIS_URL)
        self.ranked_key = "ranked_request"
    
    async def publish(self, channel: str, message: dict) -> None:
        """Publish a message to a Redis channel"""
        redis_con = Redis(connection_pool=self.redis_pool)
        await redis_con.publish(channel,pickle.dumps( message))
        await redis_con.close()

    async def subscribe(self, channel: str, message_handler: Callable[[str, Any], None]) -> None:
        """Subscribe to a Redis channel"""
        redis_con = Redis(connection_pool=self.redis_pool)
        pubsub = redis_con.pubsub()
        await pubsub.subscribe(channel)

        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = pickle.loads(message['data'])
                message_handler(channel, data)

    async def this_data(self, data: dict, time: int = 10, key: str = None) -> None:
        """Cache the dict as pickle, with a default key being the _id key in the data.
        
        Args:
            data (dict): any data
            time (int): time to store the data for (in minutes)
            key (str): key for the data
        """
        """ 
        redis_con = Redis(connection_pool=self.redis_pool)
        if key is None:
            key = data["_id"]
        await redis_con.set(key, pickle.dumps(data))
        await redis_con.expire(key, 60 * time)
        await redis_con.close()
        """
        pass

    async def get_data(self, key: str) -> dict:
        """Retrieve an existing cached data
        
        Args:
            key (str): key for the data
        
        Returns:
            dict: the data you asked for
        """
        redis_con = Redis(connection_pool=self.redis_pool)
        data = await redis_con.get(key)
        data = pickle.loads(data) if data else None
        await redis_con.close()
        return data

    async def is_cached(self, key: str) -> bool:
        """Return if the key exists
        
        Args:
            key (str): key for the data
        
        Returns:
            bool: True if the key exists, False otherwise
        """
        redis_con = Redis(connection_pool=self.redis_pool)
        exists = await redis_con.exists(key)
        await redis_con.close()
        return bool(exists)

    async def delete(self, key: str) -> None:
        """Delete a key
        
        Args:
            key (str): key for the data
        """
        redis_con = Redis(connection_pool=self.redis_pool)
        await redis_con.delete(key)
        await redis_con.close()
    
    async def create_fight(self,request):
        await self.publish("match_queue",request)

    async def close(self):
        """Disconnect the Redis pool"""
        self.redis_pool.disconnect()