import asyncio
import pickle
import datetime
import json

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from singularitybot.models.database.maindatabase import Database
from singularitybot.models.gameobjects.galaxy import Galaxy

with open("singularitybot/data/raids/current_raid.json") as file:
    current_raid = json.load(file)

# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)

async def main():
    await check_active_raids()
async def check_active_raids():
    while True:
        await asyncio.sleep(3600)  # Check every hour

        galaxies = await database.get_all_galaxies()
        for galaxy in galaxies:
            galaxy = await database.get_galaxy_info(galaxy["_id"])
            if datetime.datetime.utcnow() >= galaxy.end_of_raid:
                await process_raid_end(galaxy)

async def process_raid_end(galaxy: Galaxy):
    target_damage = current_raid["target_damage"]
    raid_successful = galaxy.damage_to_current_raid >= target_damage

    if raid_successful:
        for reward in current_raid["rewards"]:
            galaxy.items.append(reward)
        for user_id in galaxy.raid_attacks:
            user = await database.get_user_info(user_id)
            user.fragments += FRAGMENTSGAIN
            for char in user.main_characters:
                char.xp += CHARACTER_XPGAINS
            await user.update()

    # Reset raid damage and clear raid attacks
    galaxy.damage_to_current_raid = 0
    galaxy.raid_attacks = []

    # Record the result
    raid_id = f"raid_{galaxy.id}"
    record_data = {
        "raid_id": raid_id,
        "galaxy_id": galaxy.id,
        "damage": galaxy.damage_to_current_raid,
        "successful": raid_successful,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "participants": galaxy.raid_attacks,
        "rewards": current_raid["rewards"] if raid_successful else []
    }
    await database.add_raid_record(raid_id, record_data)

    # Update the galaxy info
    await galaxy.update()

if __name__ == "__main__":
    asyncio.run(main())
