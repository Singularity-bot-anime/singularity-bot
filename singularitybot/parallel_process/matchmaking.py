import asyncio
import random
import pickle

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from singularitybot.models.database.maindatabase import Database
from singularitybot.utils.functions import create_ranked_fight_request, wait_for_fight_end, create_fight_handler_request

# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)

MATCHMAKING_QUEUE = "matchmaking_requests"
MATCHLEAVE_REQUEST = "matchleave_requests"

async def main():
    requests = asyncio.Queue()
    leave_requests = asyncio.Queue()
    redis_con = Redis(connection_pool=database.redis_pool)

    async with redis_con.pubsub() as pubsub:
        await pubsub.subscribe(MATCHMAKING_QUEUE, MATCHLEAVE_REQUEST)
        task = asyncio.create_task(reader(pubsub, requests, leave_requests))
        
        while True:
            # Check for leave requests  
            while leave_requests.qsize():
                leave_request = await leave_requests.get()
                player_to_remove = pickle.loads(leave_request["data"])
                temp_queue = asyncio.Queue()
                while requests.qsize():
                    player = await requests.get()
                    player = pickle.loads(player["data"])
                    if player["player"] != player_to_remove["player"]:
                        await temp_queue.put(pickle.dumps(player))
                requests = temp_queue

            # Wait for at least two players in the queue
            if requests.qsize() >= 2:
                
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

                await database.publish(f"{player1['player']}_match_found", "match_found")
                await asyncio.sleep(0.5)
                await database.publish(f"{player2['player']}_match_found", "match_found")
                await database.create_fight(match_request)

            await asyncio.sleep(0.5)
# reader 
async def reader(channel: redis.client.PubSub, requests: asyncio.Queue, leave_requests: asyncio.Queue):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            if message["channel"].decode() == MATCHLEAVE_REQUEST:
                await leave_requests.put(message)
            else:
                await requests.put(message)

if __name__ =="__main__":
    asyncio.run(main())