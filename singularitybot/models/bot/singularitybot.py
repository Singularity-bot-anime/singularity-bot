import json
import asyncio
import disnake
import subprocess
import pickle

from disnake.ext import commands
from redis.asyncio import Redis
import redis.asyncio as redis

from singularitybot.utils.functions import wait_for
from singularitybot.models.database.maindatabase import Database
from singularitybot.models.gameobjects.character import get_character_from_template
from singularitybot.ui.fight.fight_ui import FightUi
from singularitybot.ui.place_holder import PlaceHolder

class SingularityBot(commands.AutoShardedInteractionBot):
    """AutoShardedBot with added methods and caveats"""

    def __init__(self, debug: bool = False, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        super().__init__(
            max_messages=1000000,
            loop=loop,
            reload=debug
        )
        self.developers = [
            242367586233352193,  # EIRBLAST
            112866272106012672,  # Arkkos
            399948632201232384,  # Kyoto
            228399446759702528,  # Pozymandiaz
        ]
        self.testers = self.developers + [
            248492672979959809,  # EIRBOT
        ]
        self.give_character = self.developers + []
        self.database: Database = Database(loop)
        with open("singularitybot/data/templates/characters.json", "r") as item:
            self.character_file: dict = json.load(item)["characters"]
        empty_list = [[] for _ in range(len(self.character_file))]
        self.obj_characters = list(map(get_character_from_template,self.character_file,empty_list,empty_list))
        self.avatar_url = "https://media.singularityapp.online/images/assets/pfpsister.png"
        self.bot_init = False
    async def refresh_msg(self, msg: disnake.Message) -> disnake.Message:
        """This function just refreshes a message."""
        old_msg = msg
        try:
            channel_1 = await self.fetch_channel(msg.channel.id)
        except disnake.errors.NotFound:
            channel_1 = self.get_channel(msg.channel.id)
            if channel_1 is None:
                return old_msg
        try:
            msg = await channel_1.fetch_message(msg.id)
        except disnake.errors.NotFound:
            msg: disnake.PartialMessage = channel_1.get_partial_message(msg.id)
            msg = await msg.fetch()
            if msg is None:
                return old_msg
        else:
            return msg if msg is not None else old_msg
    
    def start_fight_handler(self) -> subprocess.CompletedProcess:
        """Start the fighthandler.py script as a separate process."""
        process = subprocess.Popen(["python", "singularitybot/parallel_process/fighthandler.py"], text=True)
        print("Fight Handler Started")
        return process
    
    def start_fight_listeners(self)->None:
        """Start the listeners for the fights handler"""
        asyncio.create_task(self.handle_redis_messages(f"shard-{self.shard_id}"))

    def start_matchmaking(self) -> subprocess.CompletedProcess:
        """Start the matchmaking.py script as a separate process."""
        process = subprocess.Popen(["python", "singularitybot/parallel_process/matchmaking.py"], text=True)
        print("Matchmaking Started")
        return process
    def start_raidender(self) -> subprocess.CompletedProcess:
        """Start the matchmaking.py script as a separate process."""
        process = subprocess.Popen(["python", "singularitybot/parallel_process/raid_end.py"], text=True)
        print("Raid cleaner Started")
        return process
    def start_daily(self) -> subprocess.CompletedProcess:
        """Start the matchmaking.py script as a separate process."""
        process = subprocess.Popen(["python", "singularitybot/parallel_process/daily.py"], text=True)
        print("daily Started")
        return process
    def start_warmatchmaking(self) -> subprocess.CompletedProcess:
        """Start the matchmaking.py script as a separate process."""
        process = subprocess.Popen(["python", "singularitybot/parallel_process/warmatchmaking.py"], text=True)
        print("Galaxy War Matchmaking Started")
        return process
        
    async def handle_redis_messages(self, channel_name: str):
        print("Started actions handler shard: ",self.shard_id)
        requests = asyncio.Queue()
        asyncio.create_task(self.process_redis_message(requests))
        redis_con = Redis(connection_pool=self.database.redis_pool)
        async with redis_con.pubsub() as pubsub:
            await pubsub.subscribe(channel_name)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    await requests.put(message)
                    
    async def process_redis_message(self,requests:asyncio.Queue):
        while True:
            request = await requests.get()
            data = pickle.loads(request["data"])
            action = data.get('action')
            if action == 'send':
                asyncio.create_task( self.handle_send(data) )
            elif action == 'edit':
                asyncio.create_task( self.handle_edit(data) )
            elif action == 'edit_ui':
                asyncio.create_task( self.handle_edit_ui(data) )
            elif action == 'delete':
                asyncio.create_task( self.handle_delete(data) )

    async def handle_send(self, data: dict):
        channel = self.get_partial_messageable(data['channel_id'],type=disnake.ChannelType.text)
        if channel:
            embed = disnake.Embed.from_dict(data["embed"])
            message = await channel.send(embed=embed)
            response = {'messages': message.id, 'fight_id': data['fight_id']}
            await self.database.publish(f"{data['fight_id']}_message_response", response)

    async def handle_edit(self, data: dict):
        message = await self.get_or_fetch_message(data["message_id"])
        embed = disnake.Embed.from_dict(data["embed"])
        embed.set_image(url=data["url"])
        await message.edit(embed=embed)
        response = {'message_id': message.id, 'fight_id': data['fight_id']}
        await self.database.publish(f"{data['fight_id']}_edit_response", response)

    async def handle_edit_ui(self, data: dict):
        message = await self.get_or_fetch_message(data["message_id"])
        embed = disnake.Embed.from_dict(data["embed"]) 
        if data["view"]["type"] == "FightUi":
            watcher_characters = data["view"]["watcher_characters"]
            player_characters = data["view"]["player_characters"]
            view = FightUi(int(data["view"]["user_id"]),watcher_characters,player_characters)
            await message.edit(embed=embed, view=view)
            await view.wait()
        elif data["view"]["type"] == "placeholder":
            view = PlaceHolder()
            await message.edit(embed=embed, view=view)
        response = {'message_id': message.id, 'fight_id': data['fight_id'],"value":view.value}
        await self.database.publish(f"{data['fight_id']}_ui_response", response)

    async def handle_delete(self, data: dict):
        message = await self.get_or_fetch_message(data["message_id"])
        await message.delete()
        response = {'message_id': message.id, 'fight_id': data['fight_id']}
        await self.database.publish(f"{data['fight_id']}_delete_response",response)

    async def get_or_fetch_message(self,    message_id):
        message = self.get_message(message_id)
        if message is None: 
            await self.fetch_message(message_id)
        return message