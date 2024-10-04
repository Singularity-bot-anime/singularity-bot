import disnake
import datetime
import random
import io
import asyncio
from PIL import Image, ImageDraw
from disnake.ext import commands

from singularitybot.utils.decorators import energy_check,database_check
from singularitybot.globals.variables import DONOR_ADV_WAIT_TIME,NORMAL_ADV_WAIT_TIME,PLAYER_XPGAINS,CHARACTER_XPGAINS  
from singularitybot.globals.emojis import CustomEmoji
from singularitybot.utils.functions import secondsToText,wait_for,create_fight_handler_request,wait_for_fight_end
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.items import get_item_from_template,item_from_dict
from singularitybot.models.gameobjects.map import Map
from singularitybot.ui.paginator import Menu 
from singularitybot.ui.pve.mapmove import MoveView
from singularitybot.ui.place_holder import PlaceHolder

turorial_embed=disnake.Embed(title="Welcome to the singularity", description="This give you the basic commands and mechanics of the bot, if you want to see this again use `/adventure tutorial` use `/profile` to see your status", color=disnake.Color.dark_purple())
turorial_embed.add_field(name=f"Get new characters ✨", value=f"Summoning new character require super fragments {CustomEmoji.SUPER_FRAGMENTS}, use `/banner view` to see the current active banners. And use `/banner pull [name of the banner]` to pull a new character", inline=True)
turorial_embed.add_field(name=f"Repeatable pve 🧟", value=f"Some pve commands can be used every so often, use `/wormehole` to face random ennemies based on your level. Towers are based of anime or banners. They are a trial of endurance. The Higher you go in the tower the better the rewards use `/tower` to acces one", inline=True)
turorial_embed.add_field(name=f"Manage your characters 📦", value=f"Managing your team is essential to win. use the `/character` command to manage your characters, `/items` to manage items", inline=True)
turorial_embed.add_field(name=f"Team up 👥", value=f"The bot has a ''Clan'' system called galaxies, create or join one using `/galaxy create` or `/galaxy join` you will gain acces to new rewards and Galaxy wars !", inline=True)
turorial_embed.add_field(name=f"fight players ⚔️", value=f"The goal of the bot is to create a meaningfull pvp experience. We have 3 fight command `/fight local [tag someone]` to fight your friends, `/fight ranked` to fight somone from a different server, and `/fight test` where you fight a target dummy to test you team", inline=True)
turorial_embed.add_field(name=f"Item up 💰", value=f"The `/item` commands allow you to equip unequip and see your items. to farm up some items use `/adventure enter` wager your energy in exange for moves.", inline=True)

turorial_embed.set_footer(text="Good luck !")

class Adventure(commands.Cog):
    """Adventure commands"""

    def __init__(self, bot: SingularityBot):
        self.singularitybot = bot

    @commands.slash_command(
        name="adventure",
        description="Embark on an the main adventure!",
    )
    async def adventure(self, Interaction: disnake.ApplicationCommandInteraction):
        pass  # This will handle the main command

    @adventure.sub_command(
        name="begin",
        description="Begin your adventure!",
    )
    async def begin(self, Interaction: disnake.ApplicationCommandInteraction):
        await Interaction.response.defer()
        if await self.singularitybot.database.user_in_database(Interaction.author.id):
            embed = disnake.Embed(color=disnake.Color.dark_purple(),title="You are already registered !")
            await Interaction.send(embed=embed)
            return
        # page 1
        embed1 = disnake.Embed(color=disnake.Color.dark_purple())
        embed1.set_image(url="https://media.singularityapp.online/images/quests/begin/1.jpg")
        # page 2
        embed2 = disnake.Embed(color=disnake.Color.dark_purple())
        embed2.set_image(url="https://media.singularityapp.online/images/quests/begin/2.jpg")
        # page 3
        embed3 = disnake.Embed(color=disnake.Color.dark_purple())
        embed3.set_image(url="https://media.singularityapp.online/images/quests/begin/3.jpg")
        # page 4
        embed4 = disnake.Embed(color=disnake.Color.dark_purple())
        embed4.set_image(url="https://media.singularityapp.online/images/quests/begin/4.jpg")
        # page 5
        embed5 = disnake.Embed(color=disnake.Color.dark_purple())
        embed5.set_image(url="https://media.singularityapp.online/images/quests/begin/5.jpg")

        # add user 
        await self.singularitybot.database.add_user(Interaction.author.id)
        # add a sfrag
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        
        user.super_fragements += 1
        
        await user.update()

        await Interaction.send(embed=embed1,view=Menu([embed1, embed2,embed3,embed4,embed5]))

        await Interaction.channel.send(embed=turorial_embed)
    

    @adventure.sub_command(
        name="tutorial",
        description="Get a tutorial on how to play the bot!",
    )
    async def tutorial(self, Interaction: disnake.ApplicationCommandInteraction     ):
        await Interaction.response.defer()

        await Interaction.send(embed=turorial_embed)

    @adventure.sub_command( 
        name="daily",
        description="Claim your daily rewards!",
    )
    @database_check()
    async def daily(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        past_time = user.last_adventure
        now = datetime.datetime.now() + datetime.timedelta(hours=2)

        delta = now - past_time
        wait_time = DONOR_ADV_WAIT_TIME + (not user.is_donator()) * NORMAL_ADV_WAIT_TIME

        if delta.total_seconds() // 3600 < wait_time:
            wait_for = (
                datetime.timedelta(hours=wait_time) - delta
                if datetime.timedelta(hours=wait_time) > delta
                else delta - datetime.timedelta(hours=wait_time)
            )
            embed = disnake.Embed(
                title="You still need to wait to use this command",
                description="You can use {} in {}".format(
                    "/adventure daily", secondsToText(wait_for.total_seconds())
                ),
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=self.singularitybot.avatar_url)
            await Interaction.send(embed=embed)
            return
        user.last_adventure = now
        roll = random.randint(1, 100)
        bonus_fragments = 100
        embed = disnake.Embed(color=disnake.Color.dark_purple())
        embed.set_image(url=self.singularitybot.avatar_url)

        if roll < 101:
            embed.add_field(
                name="➥You have won some fragments", value=f"`{bonus_fragments}` {CustomEmoji.FRAGMENTS}"
            )
            user.fragments += bonus_fragments
        if roll < 50:
            id = 22
            item = item_from_dict(get_item_from_template({"id": id}))
            embed.add_field(
                name="➥You have won an item", value=f"`{item.name}`|{item.emoji}"
            )
            user.items.append(item)
        if roll < 2:
            embed.add_field(
                name="➥You have won ...", value=f" `1` {CustomEmoji.SUPER_FRAGMENTS}"
            )
            user.super_fragements += 1
        await Interaction.send(embed=embed)
        await user.update()
    @adventure.sub_command(
        name="dungeon",
        description="enter the main dungeon of the game"
    )
    @database_check()
    async def dungeon(self, Interaction: disnake.ApplicationCommandInteraction,energy: int):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        if energy > user.energy:
            embed = disnake.Embed(
                title="Not enough energy",
                description=f"You wagered `{energy}` ⚡ to enter the dungeon. You currently have `{user.energy}` ⚡.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=self.singularitybot.avatar_url)
            await Interaction.send(embed=embed)
            return
        
        user.energy -= energy
        level = user.missions_level
        embed = disnake.Embed(
            title=f"Welcome to the dungeon",
            description=f"You entered the dungeon level {level}. please wait while the dungeon is loading",
            color=disnake.Color.dark_purple(),
        )
        await Interaction.send(embed=embed)
        dungeon_map = Map(f"singularitybot/data/maps/map_{level}.png",f"singularitybot/data/mapdata/map_{level}.json")
        
        # create object for drawing
        AVATAR_SIZE = 128

        # get both avatars
        avatar1 = user.discord.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image = Image.open(buffer_avatar1).convert("RGBA")
        avatar_image = avatar_image.resize((16,16))

        message = None
        visited = set()
        visited.add(tuple(dungeon_map.player_position))
        while energy > 0:
            
            file = dungeon_map.render_map_with_avatar(avatar_image)
            view = MoveView(Interaction,dungeon_map.get_allowed_moves())
            embed = disnake.Embed(title=f"Map level {level}| {energy} ⚡ left",color=disnake.Color.dark_purple())
            embed.set_image(file=file)
            if message:
                embed.add_field(name="Event !",value=message)
            if Interaction.response.is_done():
                await Interaction.edit_original_message(embed=embed,view=view)
            else:
                await Interaction.response.edit_message(embed=embed,view=view)     
            await wait_for(view)
            dungeon_map.move_player(view.value)     
            
            Interaction = view.interaction
            energy -= 1
            if not dungeon_map.player_position in visited:
                #visited.add(dungeon_map.player_position)
                pass
            trigger = dungeon_map.trigger_event()

            if trigger:
                trigger,data = trigger
                if trigger == 1: # Fights
                    await Interaction.response.edit_message(embed=embed,view=PlaceHolder())
                    ennemy_data = {
                        "name":"Dungeons mob",
                        "avatar": None,
                        "main_characters": data,
                    }
                    players = [user.id, "0101"] 
                    channels = [Interaction.channel.id]*2
                    shards = [self.singularitybot.shard_id]*2
                    names = [user.discord.display_name,ennemy_data["name"]]
                    match_request = create_fight_handler_request(players,channels,shards,names)
                    match_request["IA_DATA"] = ennemy_data
                    try:
                        winner,combat_log = await asyncio.wait_for(wait_for_fight_end(self.singularitybot.database, match_request),timeout=600)
                    except asyncio.TimeoutError:
                        # If the fight times out after 10 minutes
                        embed = disnake.Embed(
                            title="Fight Timeout",
                            description="The fight took too long and has been terminated.",
                            color=disnake.Color.red(),
                        )
                        await Interaction.send(embed=embed)
                        return
                    user.xp += PLAYER_XPGAINS
                    for char in user.main_characters:
                        char.xp += CHARACTER_XPGAINS
                    if not winner.is_human:
                        energy -= 2
                        message = "You have lost and lost 2 ⚡"
                    else:
                        message = "You have defeated the monsters"
                elif trigger == 2: # Chest
                    item = random.choices(data["rewards"],weights=data["weights"],k=1)[0]
                    item = item_from_dict(get_item_from_template(item))
                    user.items.append(item)
                    message = f"You have won {item.name}{item.emoji}!"
                elif trigger == 3: # Bombs
                    energy -= 2
                    message = "You walked on a bomb and lost 2 ⚡"
                elif trigger == 4: # Exit
                    break
                else:
                    raise ValueError("Unknown trigger passed")

        user.energy += energy

        if energy <= 0:
            embed = disnake.Embed(title="You have no more energy", description="To get to the next dungeon finish this one by reaching the ladder")
            if Interaction.response.is_done():
                await Interaction.edit_original_message(embed=embed,view=PlaceHolder())
            else:
                await Interaction.response.edit_message(embed=embed,view=PlaceHolder())
            return

        embed = disnake.Embed(title="You have finished the dungeon", description="If a new dungeon is available you can select it !")
        if Interaction.response.is_done():
            await Interaction.edit_original_message(embed=embed,view=PlaceHolder())
        else:
            await Interaction.response.edit_message(embed=embed,view=PlaceHolder())
        await user.update()

def setup(bot: SingularityBot):
    bot.add_cog(Adventure(bot))
