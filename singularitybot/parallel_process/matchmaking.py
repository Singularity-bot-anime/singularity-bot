import asyncio
import random
import pickle

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from singularitybot.models.database.maindatabase import Database
from singularitybot.utils.functions import create_ranked_fight_request, wait_for_fight_end,create_fight_handler_request

# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)


MATCHMAKING_QUEUE = "matchmaking_requests"
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

            player1 = await requests.get()
            player2 = await requests.get()

            player1 = pickle.loads(player1["data"])
            player2 = pickle.loads(player2["data"])
            # Create and start the match (non-blocking)
            match_request = create_fight_handler_request(
                [player1["player"], player2["player"]],
                [player1["channel"], player2["channel"]],
                [player1["shard"], player2["shard"]],
                [player1["name"], player2["name"]],
                ranked=True,
            )
            asyncio.create_task(wait_for_fight_end(database, match_request))  # Non-blocking task

            await redis_con.publish(f"{player1['player']}_match_found", "match_found")
            await redis_con.publish(f"{player2['player']}_match_found", "match_found")

# reader 
async def reader(channel: redis.client.PubSub,requests:asyncio.Queue):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            await requests.put(message)


if __name__ =="__main__":
    asyncio.run(main())