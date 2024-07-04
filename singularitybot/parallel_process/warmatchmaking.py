import asyncio
import random
import pickle
import datetime

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from singularitybot.models.database.maindatabase import Database
from singularitybot.models.gameobjects.galaxy import Galaxy

# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)

MATCHMAKING_QUEUE = "war_matchmaking_requests"
CURRENT_WAR = "ACTIVE_WARS"

async def main():
    requests = asyncio.Queue()
    redis_con = Redis(connection_pool=database.redis_pool)
    
    async with redis_con.pubsub() as pubsub:
        await pubsub.subscribe(MATCHMAKING_QUEUE)
        asyncio.create_task(reader(pubsub, requests))
        asyncio.create_task(check_active_wars())
        while True:
            # Wait for at least two players in the queue
            while requests.qsize() < 2:
                await asyncio.sleep(0.5)  # Check every second

            galaxy1 = await requests.get()
            galaxy2 = await requests.get()

            galaxy1 = pickle.loads(galaxy1["data"])
            galaxy2 = pickle.loads(galaxy2["data"])

            # Already in the matchmaking checks !
            if await database.check_active_war(galaxy1):
                await database.publish(MATCHMAKING_QUEUE, galaxy2)
                continue
            if await database.check_active_war(galaxy2):
                await database.publish(MATCHMAKING_QUEUE, galaxy1)
                continue
            if galaxy1 == galaxy2:
                await database.publish(MATCHMAKING_QUEUE, galaxy1)
                continue

            galaxy1:Galaxy = await database.get_galaxy_info(galaxy1)
            galaxy2:Galaxy = await database.get_galaxy_info(galaxy2)
            
            now = datetime.datetime.utcnow()

            galaxy1.end_of_war = now + datetime.timedelta(days=2)
            galaxy2.end_of_war = now + datetime.timedelta(days=2)

            await galaxy1.update()
            await galaxy2.update()
            
            # Add the war to the active wars set
            await database.add_active_war(galaxy1.id,galaxy2.id)
            await database.add_active_war(galaxy2.id,galaxy1.id)

# reader 
async def reader(channel: redis.client.PubSub, requests: asyncio.Queue):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            await requests.put(message)

async def check_active_wars():
    while True:
        await asyncio.sleep(10)  # Check every 10 seconds

        async with await database.get_redis_connection() as conn:
            active_wars = await conn.hgetall(CURRENT_WAR)

            for galaxy_id, enemy_galaxy_id in active_wars.items():
                galaxy1 = await database.get_galaxy_info(galaxy_id)
                galaxy2 = await database.get_galaxy_info(enemy_galaxy_id)

                if datetime.datetime.utcnow() >= galaxy1.end_of_war:
                    await process_war_end(galaxy1, galaxy2)

async def process_war_end(galaxy1: Galaxy, galaxy2: Galaxy):
    # Calculate normalized damage
    damage1 = galaxy1.damage_to_current_war / len(galaxy1.users)
    damage2 = galaxy2.damage_to_current_war / len(galaxy2.users)

    # Determine winner and calculate rewards
    if damage1 > damage2:
        winner = galaxy1
        loser = galaxy2
    else:
        winner = galaxy2
        loser = galaxy1

    elo_diff = abs(winner.war_elo - loser.war_elo)
    elo_diff = max(5, min(20, elo_diff))

    # Update ELO
    winner.war_elo += elo_diff
    loser.war_elo -= elo_diff

    # Update vault with fragments
    winner.vault += 1000  # Example reward

    # Reset war damage
    galaxy1.damage_to_current_war = 0
    galaxy2.damage_to_current_war = 0

    # Remove active war records
    async with database.get_redis_connection() as conn:
        await conn.hdel(CURRENT_WAR, galaxy1.id)
        await conn.hdel(CURRENT_WAR, galaxy2.id)

    # Record the result
    war_id = f"{galaxy1.id}_vs_{galaxy2.id}"
    record_data = {
        "war_id": war_id,
        "winner": winner.id,
        "loser": loser.id,
        "winner_damage": damage1 if winner.id == galaxy1.id else damage2,
        "loser_damage": damage2 if loser.id == galaxy1.id else damage1,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    await database.add_war_record(war_id, record_data)

    # Update the galaxy info
    await winner.update()
    await loser.update()

if __name__ == "__main__":
    asyncio.run(main())
