import asyncio
import disnake
import random
import uuid
import pickle
import datetime
import traceback
from redis.asyncio import Redis, ConnectionPool

import redis.asyncio as redis

from typing import List, Union, Tuple, Dict
from singularitybot.globals.emojis import converter
from singularitybot.ui.fight.fight_ui import FightUi
from singularitybot.models.database.maindatabase import Database
from singularitybot.utils.functions import (
    game,
    get_character_status,
    get_turn_special,
    win,
    format_combat_log,
)
from singularitybot.globals.variables import (
    PLAYER_XPGAINS,
    CHARACTER_XPGAINS
)
from singularitybot.utils.image_generators import get_win_image
from singularitybot.models.gameobjects.character import Character
from singularitybot.models.gameobjects.ia import Ia
from singularitybot.models.database.user import User


# Initialize your database instance
LOOP = None
database: Database = Database(LOOP)

MATCH_QUEUE = "match_queue"


async def create_match(match_request: Dict):
    # Run the fight loop
    players = []
    for player in match_request["players"]:
        if str(player).startswith('0101') :
            players.append(Ia(match_request["IA_DATA"]))
        else:
            players.append(await database.get_user_info(player))
    asyncio.create_task( fight_loop(
        players,
        match_request["channels_ids"],
        match_request["shards"],
        match_request["names"],
        ranked=match_request['ranked'],
        galaxy_fight=match_request["galaxy_fight"],
        fight_id=match_request['match_id']
    ) )

async def reader(channel: redis.client.PubSub,requests:asyncio.Queue):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            await requests.put(message)

async def main_loop():
    requests = asyncio.Queue()
    redis_con = Redis(connection_pool=database.redis_pool)
    async with redis_con.pubsub() as pubsub:
        # Handle the match creation request
        await pubsub.subscribe(MATCH_QUEUE)
        future = asyncio.create_task(reader(pubsub,requests))
        while True:
            # Check that we get some request
            request = await requests.get()
            request = pickle.loads(request["data"])
            await create_match(request)

async def stop_fight(fight_id:uuid.UUID,winner_id:int,combat_log:list[str]):
    await database.publish(f'{fight_id}_stop', {
        'fight_id':fight_id,
        'winner':winner_id,
        'combat_log':combat_log
    })

async def stop_rank(database: Database, user_id: int,winner_id:int,combat_log:list[str]):
    """Publishes a message to the user's stop channel.

    Args:
        database (Database): The database instance.
        user_id (int): The ID of the user to stop ranking.
    """
    await database.publish(f"{user_id}_ranked_stop", {
        'user_id':user_id,
        'winner':winner_id,
        'combat_log':combat_log
    })


# Function to edit message on a specific shard
async def edit_ui(message: int,shard:int,channel_id:int, embed: disnake.Embed, view: dict,fight_id:uuid.UUID)->Union[list[int],int]:
    await database.publish(f'shard-{shard}', {
        'action': 'edit_ui',
        'channel_id':channel_id,
        'message_id': message,
        'embed': embed,
        'view': view,
        'fight_id':fight_id
    })
    redis_con = Redis(connection_pool=database.redis_pool)
    async with redis_con.pubsub() as pubsub:
    # Wait for the response
        await pubsub.subscribe(f"{fight_id}_ui_response")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                break
    return pickle.loads(message["data"])["value"]

async def edit(messages: List[int],shards:list[int],channels:List[int] ,embed: disnake.Embed,url:str,fight_id:uuid.UUID):
    redis_con = Redis(connection_pool=database.redis_pool)
    if channels[0] == channels[1]:
        shards = set(shards)
        channels = set(channels)
    async with redis_con.pubsub() as pubsub:
        for message,shard,channel_id in zip(messages,shards,channels):
            await database.publish(f'shard-{shard}', {
                'action': 'edit',
                'channel_id': channel_id,
                'message_id' :message ,
                'embed': embed,
                'url':url,
                'fight_id':fight_id
            })
        # Wait for the response
        await pubsub.subscribe(f"{fight_id}_edit_response")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                break

async def send_all(embed: disnake.Embed, channels: List[int],shards:list[int], fight_id: str) -> List[int]:
    messages = []
    if channels[0] == channels[1]:
        shards = set(shards)
        channels = set(channels)
    redis_con = Redis(connection_pool=database.redis_pool)
    async with redis_con.pubsub() as pubsub:
        await pubsub.subscribe(f"{fight_id}_message_response")
        for channel_id,shard in zip(channels,shards):
            await database.publish(f'shard-{shard}', {
                'action': 'send',
                'embed': embed,
                'channel_id': channel_id,
                'fight_id': fight_id
            })
            
            while True:
                # Wait for the response
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    break
            messages.append(pickle.loads(message["data"])["messages"])
    if len(messages)< 2:
        return messages[0],messages[0]
    return messages[0],messages[1]

async def delete_all(messages: List[int],shards:list[int],channels:list[int],fight_id:uuid.UUID):
    redis_con = Redis(connection_pool=database.redis_pool)
    if channels[0] == channels[1]:
        shards = set(shards)
        channels = set(channels)
    async with redis_con.pubsub() as pubsub:
        await pubsub.subscribe(f"{fight_id}_delete_response")
        for message,shard,channel_id in zip(messages,shards,channels):
            await database.publish(f'shard-{shard}', {
                'action': 'delete',
                'channel_id':channel_id,
                'message_id': message,
                'fight_id':fight_id
            })
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    break

async def fight_loop(
    fighters: List[Union[User, Ia]],
    channels: List[int],
    shards:List[int],
    names:List[str],
    ranked: bool = True,
    galaxy_fight: bool = False,
    fight_id: str = str(uuid.uuid4())
) -> Tuple[Union[User, Ia], List[str]]:
    try:
        # Message used for status and attacks
        embed = disnake.Embed(
            title=f"fight is loading please wait",
            color=disnake.Color.dark_purple(),
        )
        messages_1 = await send_all(embed, channels,shards, fight_id)
        # Message used to display specials
        embed = disnake.Embed(colour=disnake.Colour.dark_purple())
        image_list = ["https://media1.tenor.com/m/43hSW7CM0UoAAAAC/anime-come.gif",
        "https://c.tenor.com/B_J3xedKvA8AAAAC/jojo-anime.gif",
        "https://media1.tenor.com/m/_PPOYsb1GeIAAAAd/anime-fight.gif",
        "https://media1.tenor.com/m/yd7Ntm5sUHMAAAAC/sasuke-naruto.gif",
        ]
        embed.set_image(url=random.choice(image_list))
        messages_2 = await send_all(embed, channels,shards, fight_id)
        # Set the message for the player
        fighters[0].message = messages_1[0]
        fighters[1].message = messages_1[1]
        # Set up some fight variables
        combat_log = []
        turn = 0
        king_crimson = False
        # Determine who starts first
        start_1 = sum([i.current_speed for i in fighters[0].main_characters])
        start_2 = sum([i.current_speed for i in fighters[1].main_characters])
        players = [fighters[0], fighters[1]]
        if start_2 > start_1:
            players = [fighters[1], fighters[0]]
            channels = [channels[1],channels[0]]
            shars = [shards[1],shards[0]]
        elif start_2 == start_1:
            combined = list(zip(players, channels, shards,names,messages_2,messages_1))
            random.shuffle(combined)
            players, channels, shards, names,messages_2,messages_1 = zip(*combined)
            players, channels, shards, names,messages_2,messages_1 = list(players), list(channels), list(shards), list(names),list(messages_2),list(messages_1)
        # We give a little help if you start second
        for character in players[1].main_characters:
            character.special_meter += 1
        # Game loop
        
        while game(players[0].main_characters, players[1].main_characters):
            player = players[turn % 2]
            watcher = players[(turn + 1) % 2]
            for character in player.main_characters:
                if not game(players[0].main_characters, players[1].main_characters):
                    break
                if character.is_alive() and not character.is_stunned():
                    embed = disnake.Embed(
                        title="Fight",
                        description=f"Turn `{names[turn%2]}`",
                        color=disnake.Color.dark_purple(),
                    )
                    status = get_character_status(character)
                    turn_ = get_turn_special(character)
                    embed.add_field(
                        name=f"What shoud {character.name} do ?",
                        value=f"`HP`:`{int(character.current_hp)}/{int(character.start_hp)}❤️`\n`STATUS`:{status}\n`Ability`:{turn_}\n           ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
                        inline=False,
                    )
                    for ennemy_character in watcher.main_characters:
                        if ennemy_character.is_alive():
                            etoile = (
                                converter[ennemy_character.rarity] + "🌟" * character.awaken
                            )
                            status = get_character_status(ennemy_character)
                            spe = get_turn_special(ennemy_character)
                            embed.add_field(
                                name=f"`『{ennemy_character.name}』`\n{etoile}",
                                value=f"HP:`{int(ennemy_character.current_hp)}/{int(ennemy_character.start_hp)}❤️`\n`STATUS`:{status}\n`Ability`:{spe}\n    ▬▬▬▬▬▬▬▬▬",
                                inline=True,
                            )
                    if player.is_human:
                        view = view_to_dict_fight('FightUi',int(player.id),watcher.main_characters,player.main_characters)
                        if ranked:
                            await edit_ui(watcher.message,shards[(turn+1)%2],channels[(turn+1)%2], embed, {'type':'placeholder'},fight_id)
                        value = await edit_ui(player.message,shards[turn%2],channels[turn%2] ,embed,view,fight_id)
                        if value == None:
                            for i in player.main_characters:
                                i.current_hp = 0
                            combat_log.append("Combat terminated because of inactivity.")
                            break
                        
                        await edit_ui(player.message,shards[turn%2],channels[turn%2], embed,{'type':'placeholder'},fight_id)
                        if value == "ff":
                            for i in player.main_characters:
                                i.current_hp = 0
                                combat_log.append(
                                    "{}".format(turn + 1) + ", " + f"{names[turn%2]} surrendered"
                                )
                            break
                        character_index = value
                        targeted_character: Character = watcher.main_characters[character_index]
                    else:
                        await asyncio.sleep(1)
                        targeted_character: Stand = player.choice(watcher.main_characters)
                    data = character.attack(targeted_character)
                    info_message = ""
                    if data["dodged"]:
                        info_message = "{} dodged {} attack".format(
                            targeted_character.name, character.name
                        )
                    elif data["critical"]:
                        info_message = "{} was hit with a citical strike for {} damage".format(
                            targeted_character.name, data["damage"]
                        )
                    else:
                        info_message = "{} was hit with {} damage".format(
                            targeted_character.name, data["damage"]
                        )
                    combat_log.append(
                        "{}".format(turn + 1) + ", " + info_message
                    )
                    embed = disnake.Embed(
                        title=info_message, color=disnake.Color.dark_purple()
                    )
                    url=f"https://media.singularityapp.online/images/cards/{character.id}.png"  
                    await edit(messages_2,shards,channels, embed,url,fight_id)
                if character.is_alive() and not (character.is_stunned()) and character.as_special():
                    payload, message = character.special(player.main_characters, watcher.main_characters)
                    if payload["is_a_special"]:
                        await asyncio.sleep(1)
                        combat_log.append(
                            "turn {} Special Used".format(turn + 1) + ", " + message
                        )
                        embed = disnake.Embed(title=message, color=disnake.Color.dark_purple())
                        url=character.special_url
                        await edit(messages_2,shards,channels, embed,url,fight_id)
                        await asyncio.sleep(1)
                        king_crimson |= payload["king_crimson"]
                if character.is_alive():
                    for item in character.items:
                        if item.as_special():
                            message = item.special(character, player.main_characters, watcher.main_characters)
                            await asyncio.sleep(0.5)
                            if message == "None":
                                combat_log.append(
                                    "turn {} item special".format(turn + 1)
                                    + ", "
                                    + message
                                )
                                embed = disnake.Embed(
                                    title=message, color=disnake.Color.dark_purple()
                                )
                                embed.set_image(
                                    url=f"https://storage.stfurequiem.com/item_special/{item.id}.gif"
                                )
                                await edit(messages_2,shards, embed)
                                await asyncio.sleep(0.5)
            for character in player.main_characters + watcher.main_characters:
                character.end_turn()
            turn_amount = 1
            if king_crimson:
                # We set this to 2 so we don't change parity
                # Effectivly skipping a turn
                turn_amount = 2
                # Disable the effect afterward
                king_crimson = False
            turn += turn_amount
        await delete_all(messages_1,shards,channels,fight_id)
        await delete_all(messages_2,shards,channels,fight_id)
        
        if galaxy_fight:
            ia = players[0] if not players[0].is_human else players[1]
            dmg = calculate_team_damage(ia.main_characters)
            combat_log.append(dmg)
            await stop_fight(fight_id,win(players).id,combat_log)
            return

        if not ranked:
            await stop_fight(fight_id,win(players).id,combat_log)
            return
         
        winner = win(players)
        if winner == players[0]:
            looser = players[1]
        else:
            looser = players[0]
        winner.xp += PLAYER_XPGAINS * 3
        for character in winner.main_characters:
            character.xp += CHARACTER_XPGAINS * 3
        winner.fragments += 200
        winner.global_elo += min(10, max(0,winner.global_elo - looser.global_elo))
        looser.xp += PLAYER_XPGAINS
        for character in looser.main_characters:
            character.xp += CHARACTER_XPGAINS
        looser.fragments += 0
        looser.global_elo -= min(10, max(0,winner.global_elo - looser.global_elo))
        if looser.global_elo < 0:
            looser.global_elo = 0
        await winner.update()
        await looser.update()
        await stop_rank(database,winner.id,winner.id.id,combat_log)
        await stop_rank(database,looser.id,winner.id.id,combat_log)
        return 
    except Exception as error:
        if ranked:
            error_traceback = "".join(
                traceback.format_exception(
                    etype=type(error), value=error, tb=error.__traceback__
                )
            )
            await database.add_log(
                datetime.datetime.now(),
                "fight_loop",
                str(type(error)),
                str(error_traceback),
            )
        else:
            raise error

def view_to_dict_fight(type:str,user_id:int,watcher_characters:list[Character],player_characters:list[Character]) -> dict:
        return {
            'type':type  ,
            'user_id':user_id,
            'watcher_characters': watcher_characters,
            'player_characters': player_characters,
        }

def calculate_team_damage(characters: List[Character]) -> int:
    """
    Calculate the total damage done to a team at the end of a fight.
    
    Args:
        characters (List[Character]): List of characters in the team.
    
    Returns:
        int: Total damage taken by the team.
    """
    total_damage = 0
    
    for character in characters:
        damage_taken = character.start_hp - character.current_hp
        total_damage += damage_taken
    
    return total_damage

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Shutting down...")