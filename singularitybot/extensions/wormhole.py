import disnake
import random
import datetime

from typing import List
from numpy.random import choice
from disnake.ext import commands

# ui
from singularitybot.ui.paginator import Menu

# utils
from singularitybot.utils.decorators import database_check,energy_check
from singularitybot.utils.functions import secondsToText, format_combat_log,create_fight_handler_request,wait_for_fight_end

# stfu model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.character import Character, get_character_from_template
from singularitybot.models.gameobjects.ia import Ia
from singularitybot.models.gameobjects.items import item_from_dict, get_item_from_template
from singularitybot.globals.variables import (
    PLAYER_XPGAINS,
    CHARACTER_XPGAINS,
    FRAGMENTSGAIN,
    WORMHOLEURL,
    CHANCEITEM,
    DONOR_WH_WAIT_TIME,
    NORMAL_WH_WAIT_TIME,
)
from singularitybot.globals.emojis import CustomEmoji


class Wormhole(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.slash_command(
        name="wormhole", description="fight random generated characters based on your level"
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @database_check()
    @energy_check()
    async def wormhole(self, Interaction: disnake.ApplicationCommandInteraction):

        # translation
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        # Check the time
        past_time = user.last_wormhole
        now = datetime.datetime.now() + datetime.timedelta(hours=2)

        delta = now - past_time
        wait_time = DONOR_WH_WAIT_TIME + (not user.is_donator()) * NORMAL_WH_WAIT_TIME

        if delta.total_seconds() // 3600 < wait_time:
            wait_for = (
                datetime.timedelta(hours=wait_time) - delta
                if datetime.timedelta(hours=wait_time) > delta
                else delta - datetime.timedelta(hours=wait_time)
            )
            embed = disnake.Embed(
                title="Sorry but...",
                description="{} is on cooldown you need to wait {} to use it again".format(
                    "crusade", secondsToText(wait_for.total_seconds())
                ),
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(url=self.singularitybot.avatar_url)
            await Interaction.send(embed=embed)
            return
        
        if not user.main_characters:
            embed = disnake.Embed(title="You need to have main characters to fight use `/character main`",color=disnake.Colour.dark_purple())
            embed.set_image(url="https://media.singularityapp.online/images/assets/notregistered.jpg")
            await Interaction.send(embed=embed)
        
        embed = disnake.Embed(
            title="You fell into a wormhole ...", color=disnake.Color.dark_purple()
        )
        await Interaction.send(embed=embed)

        user.last_wormhole = datetime.datetime.now() + datetime.timedelta(hours=2)
        multi = 1
        if user.level < 5:
            rarity = "R"
            n = random.randint(1, 2)
        elif 5 <= user.level < 25:
            rarity = "SR"
            n = random.randint(1, 1)
            multi = 2
        elif 25 <= user.level < 50:
            rarity = "SSR"
            n = random.randint(2, 3)
            multi = 3
        elif 50 <= user.level < 75:
            rarity = "UR"
            n = 3
            multi = 3
        elif user.level >= 75:
            rarity = "LR"
            n = 3
            multi = 4
        names = ["Megalo", "Mr Davelo", "Vince", "Icarus", "Arkkos", "Yoshikage Ramsay","Keyshiwo","EIRBLAST","Obama","Mizu","ft.fate"]
        ennemy_data = {
            "name": f"{random.choice(names)}'s Soul",
            "avatar": None,
            "main_characters": [
                char.to_dict() for char in get_characters(self.singularitybot, rarity=rarity, n=n)
            ],
        }
        players = [user.id, "0101"]
        channels = [Interaction.channel.id]*2
        shards = [self.singularitybot.shard_id]*2
        names = [user.discord.display_name,ennemy_data["name"]]
        match_request = create_fight_handler_request(players,channels,shards,names)
        match_request["IA_DATA"] = ennemy_data
        winner,combat_log = await wait_for_fight_end(self.singularitybot.database,match_request)
        
        embeds = format_combat_log(combat_log)
        final_view = Menu(embeds)
        await Interaction.channel.send(embed=embeds[0], view=final_view)
        # Loose
        if not winner.is_human:
            embed = disnake.Embed(
                title="The wormhole spits you out, without any rewards", color=disnake.Color.purple()
            )
            embed.set_thumbnail(url=self.singularitybot.avatar_url)
            await Interaction.channel.send(embed=embed)
            await user.update()
            return
        # Win
        user = winner
        # Guarented drops and stuff
        user.xp += PLAYER_XPGAINS
        user.fragments += FRAGMENTSGAIN * multi
        for char in user.main_characters:
            char.xp += CHARACTER_XPGAINS * multi
        embed = disnake.Embed(
            title="You vanquished the wormhole !", color=disnake.Color.dark_purple()
        )
        embed.set_image(url=WORMHOLEURL)
        embed.add_field(
            name="You gained fragments",
            value=f"`{FRAGMENTSGAIN*multi}`{CustomEmoji.FRAGMENTS}",
        )
        item_roll = random.randint(1, 100)
        if item_roll <= 5:
            id = random.choice([1, 2, 3,22])
            item = item_from_dict(get_item_from_template({"id": id}))
            embed.add_field(
                name="You have won an item", value=f"`{item.name}|`{item.emoji}"
            )
            user.items.append(item)
        await user.update()
        await Interaction.channel.send(embed=embed)


def get_characters(singularitybot: SingularityBot, rarity='SR', n: int = 1) -> List[Character]:
    leveled = [char for char in singularitybot.character_file if char["rarity"] == rarity]
    random_chars = [get_character_from_template(char,[],[]) for char in choice(leveled, size=n)]
    return random_chars


def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Wormhole(singularitybot))