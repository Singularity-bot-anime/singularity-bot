import disnake
import asyncio
import random
import requests
import uuid
import pickle


from typing import List, Union, TYPE_CHECKING
from discord.ext import commands
from redis.asyncio import Redis, ConnectionPool

import redis.asyncio as redis

# It's for typehint
if TYPE_CHECKING:
    from singularitybot.models.gameobjects.character import Character

from singularitybot.models.gameobjects.ia import Ia
from singularitybot.models.gameobjects.effects import Effect, EffectType
from singularitybot.models.database.user import User
from singularitybot.models.database.maindatabase import Database
from singularitybot.globals.emojis import CustomEmoji,converter
from singularitybot.ui.cancelbutton import Cancel

MATCHLEAVE_REQUEST = "matchleave_requests"


# playing one or multiple file a better version of playfile bassicly
async def play_files(
    ctx: Union[commands.Context, disnake.ApplicationCommandInteraction],
    files: List[str],
):
    """
    takes a list of url and play them
    if no voice channel is find do nothing
    """
    voice_channel = ctx.author.voice
    # check if the author is connected
    if voice_channel is not None:
        try:
            # grab the channel
            voice = await ctx.author.voice.channel.connect()
        except disnake.errors.ClientException:
            # this error mean the client already connected
            # which can happen
            # get the voicestate
            voice = ctx.me.voice.channel.voice_states.get(ctx.me.id)
        # play every file in chains
        for url in files:
            source = disnake.FFmpegPCMAudio(url)
            voice.play(source)
            # wait untill the bot is finish playing
            while voice.is_playing():
                await asyncio.sleep(0.1)
        await voice.disconnect()
    # this render the fonction callable even if the person is not connected


# Used in UI and embeds
def sign(x: int):
    if x > 0:
        return f"(+{int(x)})"
    elif x < 0:
        return f"(-{int(x)})"
    else:
        return ""

#Determine if a fight should keep going or not
def game(stand1: List["Stand"], stand2: List["Stand"]) -> bool:
    result = False
    for stand in stand1:
        result |= stand.is_alive()
    result2 = False
    for stand in stand2:
        result2 |= stand.is_alive()
    return result and result2

#get a list of effect emojis
def get_character_status(character: "Character") -> str:
    status = ""
    if not character.effects:
        status = " `✔️` "
        if character.taunt:
            status = "🎯"
    else:
        status = ""
        if character.taunt:
            status += "🎯"
        unique: List[Effect] = []
        actual_effect = character.effects
        if character.current_armor < character.start_armor:
            actual_effect.append(Effect(EffectType.WEAKEN, 1, 0))
        if character.current_damage > character.start_damage:
            actual_effect.append(Effect(EffectType.DAMAGEUP,1,0))
        if character.current_hp > character.start_hp:
            actual_effect.append(Effect(EffectType.HEALTHBOOST,1,0))
        if character.current_speed < character.start_speed:
            actual_effect.append(Effect(EffectType.SLOW, 1, 0))
        for effect in character.effects:
            if effect.type not in [e.type for e in unique]:
                unique.append(effect)
        for effect in unique:
            status += f" {effect.emoji}"
    return status

# get the number of turn until the ability
def get_turn_special(character: "Character") -> str:
    turn = character.turn_for_ability - character.special_meter
    if turn > 0:
        return f"in {turn} turn"
    return "ready ✔️"


def win(players: List[Union[User, Ia]]) -> User:
    """Determine who won between two players

    Args:
        players (List[User]): The User who fought

    Returns:
        User: The User who won
    """
    alive_status_1 = False
    for character in players[0].main_characters:
        alive_status_1 |= character.is_alive()
    alive_status_2 = False
    for character in players[1].main_characters:
        alive_status_2 |= character.is_alive()
    if alive_status_1 and not alive_status_2:
        return players[0]
    else:
        return players[1]


# used in cooldown functions
def secondsToText(seconds):
    seconds = int(seconds)
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    final_s = ""
    final_s += f"{days} days, " if days > 0 else ""
    final_s += f"{hour} hour, " if hour > 0 else ""
    final_s += f"{minutes} minutes, " if minutes > 0 else ""
    final_s += f"{seconds} seconds" if seconds > 0 else ""
    return final_s

def format_combat_log(combat_log: List[str]) -> List[disnake.Embed]:
    embeds = []
    embed = disnake.Embed(title="Fight combat log", color=disnake.Color.purple())
    for i, line in enumerate(combat_log):
        if len(embed.fields) >= 8:
            embeds.append(embed)
            embed = disnake.Embed(
                title="Fight combat log", color=disnake.Color.purple()
            )
        embed.add_field(name=line, value=f"Turn n°{i}",inline=True)
    embeds.append(embed)
    return embeds


async def wait_for(view: disnake.ui.View):
    if await view.wait():
        raise asyncio.TimeoutError


# get a drop from a list
def get_drop_from_list(stand_list: List["Stand"], number_of_drop: int = 1) -> list:
    stand_list = [stand for stand in stand_list if stand.stars != 10]
    # count the stand per star category
    nums = [1, 1, 1, 1, 1, 1]
    for i in stand_list:
        nums[i.stars - 1] += 1
    # probability pondered by the number of stand in the star category
    stars = [1, 2, 3, 4, 5, 6]
    weights = [
        0.35,
        0.3,
        0.2,
        0.1,
        0.04,
        0.01,
    ]
    star = random.choices(stars, weights=weights, k=1)[0]

    stand_list = [stand for stand in stand_list if stand.stars == star]
    # return one of the stand
    drops = random.choices(stand_list, k=number_of_drop)
    return drops


def add_to_available_storage(user: User, character: "Character", skip_main:bool=False):
    if len(user.main_characters) < 3 and not skip_main:
        user.main_characters.append(character)
        return "Main Characters Storage"
    if len(user.character_storage) < 25:
        user.character_storage.append(character)
        return "Character storage"
    if len(user.pcharacter_storage) < 25 and user.is_donator():
        user.pcharacter_storage.append(character)
        return "Premium Character storage"
    return False


def character_field(character: "Character", embed: disnake.Embed):
    _rarity = converter[character.rarity] + "🌟" * character.awaken
    typequal=""
    for _t,_q in zip(character.etypes,character.equalities):
        typequal+=f"{_t.emoji}{_q.emoji}  "
    field_value = (     f"➥ __Name__ **[ **{character.name} **]**\n"+
                        f"➥ __Level__ **[ **{character.level} **]**\n"+
                        f"➥ __Rarity__ **[ **{converter[character.rarity]} **]**\n"+
                        f"➥ __Qualities__ **[ **{typequal}** ]**\n"+
                        f"➥ __Universe__ **[ **{character.universe}** ]**")
    embed.add_field(
        name="▬▬▬`CHARACTER`▬▬▬",
        value=field_value + "▬▬▬▬▬▬▬▬▬",
        
    )
    embed.add_field(
        name="▬▬▬`STATS`▬▬▬",
        value=f"HP:`{int(character.current_hp)}❤️`\n"
        + f"DAMAGE:`{int(character.current_damage)}⚔️`\n"
        + f"ARMOR:`{int(character.current_armor)}🛡️`\n"
        + f"SPEED:`{int(character.current_speed)}💨`\n"
        + f"XP:`{int(character.xp)}`\n▬▬▬▬▬▬▬▬▬",
    )
    embed.add_field(
        name="▬▬`SPECIAL`▬▬",
        value=character.special_description + "\n▬▬▬▬▬▬▬▬▬",
    )
    if character.taunt:
        embed.add_field(
            name="▬▬`TAUNT`▬▬",
            value="🎯 this character will take damage first from basic attack before it's teamate" + "\n     ▬▬▬▬▬▬▬▬▬",
        )
    if len(character.items) != 0:
        item = ""
        for i in character.items:
            item += f"{i.emoji}:{i.name}\n"
        item += "    ▬▬▬▬▬▬▬▬▬\n"
        embed.add_field(name="▬▬▬`ITEMS`▬▬▬", value=item)
    embed.set_image(url=f"https://media.singularityapp.online/images/cards/{character.id}.png")
    return embed


def is_url_image(image_url: str):
    image_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif")
    try:
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
        return False
    except:
        return False

def create_fight_handler_request(players:list[int],channels_ids:list[int],shards:list[int],names:list[str] = ["Unknown","Unknown"], ranked=False,galaxy_fight=False,galaxy_raid=False)->dict:
    """helper fonction to create a request

    Args:
        players (list[int]): a list of the player id
        channels_ids (list[int]): a list of the channels where the fights must take place
        shards (list[int]): the shard where the fight takes place
        ranked (bool, optional): wheter the fight a ranked (and reward should be appliedin the handler). Defaults to False.

    Returns:
        dict: the formated request
    """
    request = {
        "ranked":ranked,
        "match_id":uuid.uuid1(),
        "players":players,
        "channels_ids":channels_ids,
        "shards":shards,
        "names":names,
        "galaxy_fight":galaxy_fight,
        "galaxy_raid":galaxy_raid
    }   
    return request

def create_ranked_fight_request(player:int,channel:int,shard:int,name:int,elo:int)->dict:
    """return a formated request for the matchmaking queue

    Args:
        player (int): player id
        channel (int): channel id
        shard (int): shard id
        name (int): the name of the player

    Returns:
        dict: the formated request
    """
    request = {
        "player":player,
        "channel":channel,
        "shard":shard,
        "name":name
    }
    return request

async def wait_for_fight_end(database:Database,match_request:dict):
    """This coroutine as 2 role, start a fight and wait for it's result

    Args:
        database (Database): an instance of the class database
        match_request (dict): the request formated by `create_fight_handler_request()`

    Returns:
        tupple: a tupple with the result of the fight
    """
    id = match_request["match_id"]
    # send the request to the fight handler
    await database.create_fight(match_request)
    redis_con = await database.get_redis_connection()
    async with redis_con.pubsub() as pubsub:
    #Wait for the fight to end and it's results
        await pubsub.subscribe(f"{id}_stop")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                break

    fight_results = pickle.loads(message["data"])
    combat_log = fight_results["combat_log"]
    winner = fight_results["winner"]

    if str(winner).startswith('0101') :
        winner = Ia(match_request["IA_DATA"])
    else:
        winner = await database.get_user_info(winner)

    return winner,combat_log

async def reader(channel: redis.client.PubSub, requests: asyncio.Queue):
    try:
        while True: 
            message = await channel.get_message(ignore_subscribe_messages=True)
            if message is not None:
                await requests.put(message)
    except (asyncio.CancelledError,redis.ConnectionError):
        return None 

async def wait_for_match(database: Database, interaction: disnake.ApplicationCommandInteraction) -> bool:
    """Waits for a match to be found or cancellation.

    This function now includes the Confirm view for cancellation directly within it.

    Args:
        database (Database): The database instance.
        interaction (disnake.ApplicationCommandInteraction): The interaction to send messages and the view to.

    Returns:
        bool: True if a match was found, False if the user canceled or timeout.
    """
    channel_name = f"{interaction.author.id}_match_found"
    redis_con = Redis(connection_pool=database.redis_pool)
    
    view = Cancel(interaction, timeout=0)
    embed = disnake.Embed(title=f"Matchmaking Queue {CustomEmoji.LOADING_ICON}", description="Looking for an opponent", color=disnake.Color.dark_purple())
    embed.set_image(url="https://media1.tenor.com/m/2OA-uQTBCBQAAAAd/detective-conan-case-closed.gif")
    await interaction.edit_original_message(embed=embed, view=view)

    async with redis_con.pubsub() as pubsub:
        await pubsub.subscribe(channel_name)
        requests = asyncio.Queue()
        reader_task = asyncio.create_task(reader(pubsub, requests))
        # Let the reader start up
        await asyncio.sleep(1)
        start_time = asyncio.get_event_loop().time()
        timeout = 60 * 5  # 5 minutes

        while True:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > timeout:
                await redis_con.publish(MATCHLEAVE_REQUEST, pickle.dumps({"player": interaction.author.id}))
                reader_task.cancel()
                return False  # Timeout
        
            if requests.qsize():
                reader_task.cancel()
                interaction = view.interaction
                await interaction.delete_original_message()
                embed.add_field(name=f"{interaction.author.mention}",value="A match was found")
                await interaction.channel.send(embed=embed)
                return True  # Match found     

            if view.value is True:  # The view has been interacted with and cancel button was pressed
                await redis_con.publish(MATCHLEAVE_REQUEST, pickle.dumps({"player": interaction.author.id}))
                reader_task.cancel()
                return False  # User canceled

            await asyncio.sleep(0.5)  # Small sleep to prevent tight loop


async def wait_for_ranked_stop(database:Database,user_id:int):
    """This coroutine wait for a ranked match to end

    Args:
        database (Database): an instance of the class database
        match_request (dict): the request formated by `create_fight_handler_request()`

    Returns:
        tupple: a tupple with the result of the fight
    """
    
    redis_con = Redis(connection_pool=database.redis_pool)
    async with redis_con.pubsub() as pubsub:
    #Wait for the fight to end and it's results
        await pubsub.subscribe(f"{user_id}_ranked_stop")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                break
    fight_results = pickle.loads(message["data"])
    combat_log = fight_results["combat_log"]
    winner = fight_results["winner"]

    if str(winner).startswith('0101') :
        winner = Ia(match_request["IA_DATA"])
    else:
        winner = await database.get_user_info(winner)

    return winner,combat_log

async def view_timeout(interaction: disnake.ApplicationCommandInteraction):
    """add an expired button to views

    Args:
        interaction (disnake.ApplicationCommandInteraction): [description]
    """
    view = disnake.ui.View()
    view.add_item(
        disnake.ui.Button(
            label=f"Expired",
            emoji="⌚",
            style=disnake.ButtonStyle.grey,
            disabled=True,
        )
    )
    try:
        await interaction.edit_original_message(view=view)
    except:
        try:
            await interaction.response.edit_message(view=view)
        except:
            pass
        pass
