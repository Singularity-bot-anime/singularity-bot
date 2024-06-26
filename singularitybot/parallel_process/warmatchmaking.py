import asyncio
import random
import pickle

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from singularitybot.models.database.maindatabase import Database

# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)


MATCHMAKING_QUEUE = "war_matchmaking_requests"
async def main():
    requests = asyncio.Queue()
    redis_con = Redis(connection_pool=database.redis_pool)

    async with redis_con.pubsub() as pubsub:
        await pubsub.subscribe(MATCHMAKING_QUEUE)
        future = asyncio.create_task(reader(pubsub, requests))

        while True:
            # Wait for at least two players in the queue
            while requests.qsize() < 2:
                await asyncio.sleep(0.5)  # Check every second

            galaxy1 = await requests.get()
            galaxy2 = await requests.get()

            galaxy1 = pickle.loads(player1["data"])
            galaxy2 = pickle.loads(player2["data"])
            # Create and start the war (non-blocking)
            

# reader 
async def reader(channel: redis.client.PubSub,requests:asyncio.Queue):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            await requests.put(message)


if __name__ =="__main__":
    asyncio.run(main())