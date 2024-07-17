import asyncio
import pickle
import datetime
import json
import datetime

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from singularitybot.models.database.maindatabase import Database

# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)

async def main():
    while True:
        await asyncio.sleep(3600)  # Check every hour
        # do the opration on user that need to happen
        async with await database.get_redis_connection() as conn:
            user_ids = await conn.hkeys("users")
            for user_id in user_ids:
                user = await database.get_user_info(user_id)
                now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                wait_time = (12 - 6*user.is_donator()) * 60 * 60
                # Check if 24 hours have passed since last energy replenishment
                if (now - user.last_full_energy).total_seconds() >= wait_time and user.energy < user.total_energy:
                    user.energy = user.total_energy  # Replenish energy
                    user.last_full_energy = now
                    await user.update()
                


if __name__ == "__main__":
    asyncio.run(main())