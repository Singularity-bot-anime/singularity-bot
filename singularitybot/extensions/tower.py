import disnake
import json
import random
import asyncio

from disnake.ext import commands

# ui
from singularitybot.ui.pve.tower_select import TowerSelectDropdown
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.place_holder import PlaceHolder

# utils
from singularitybot.utils.decorators import database_check
from singularitybot.utils.functions import secondsToText, format_combat_log,create_fight_handler_request,wait_for_fight_end
from singularitybot.utils.functions import wait_for
from singularitybot.utils.image_generators import tower_images

# stfu model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.ia import Ia
from singularitybot.models.gameobjects.items import item_from_dict, get_item_from_template
from singularitybot.globals.variables import (
    PLAYER_XPGAINS,
    CHARACTER_XPGAINS,
    ENTRYCOST,
    TOWERURL,
)
from singularitybot.globals.emojis import CustomEmoji


class Tower(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot
        with open("singularitybot/data/towers/towers.json", "r") as item:
            self.tower_file = json.load(item)["towers"]

    @commands.slash_command(
        name="tower", description="Enter towers to farm items and new character !"
    )
    @database_check()
    async def tower(self, Interaction: disnake.ApplicationCommandInteraction):
        # translation
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        # Check entry cost

        entry = f"{ENTRYCOST}{CustomEmoji.FRAGMENTS}"
        balance = f"{user.fragments}{CustomEmoji.FRAGMENTS}"
        embed = disnake.Embed(
            title="Do you want to enter the tower ? an Entry cost: {}, you have {}".format(entry, balance),
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=TOWERURL)
        view = Confirm(Interaction)

        await Interaction.send(embed=embed, view=view)
        await wait_for(view)

        Interaction = view.interaction

        if not view.value:
            embed = disnake.Embed(
                title="You did not enter the tower", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=TOWERURL)
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return
        if user.fragments < ENTRYCOST:
            amount = f"{ENTRYCOST-user.fragments}{CustomEmoji.FRAGMENTS}"
            embed = disnake.Embed(
                title="You don't have enought fragments you need {} more".format(amount),
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=TOWERURL)
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return

        # Level selection

        user.fragments -= ENTRYCOST
        #await user.update()
        view = TowerSelectDropdown(Interaction)
        await Interaction.response.edit_message(embed=embed, view=view)
        await wait_for(view)
        tower_id = view.value -1
        tower = self.tower_file[tower_id]

        # fights
        for i, main_characters in enumerate(tower["fighters"]):
            file = await tower_images[f"{tower_id+1}"](user.discord, i + 1)
            embed = disnake.Embed(color=disnake.Color.dark_purple())
            embed.set_image(file=file)

            Stage = await Interaction.channel.send(embed=embed)

            await asyncio.sleep(5)

            await Stage.delete()

            ennemy_data = {
                "name": f"{tower['names'][i]}",
                "avatar": None,
                "main_characters": main_characters,
            }

            players = [user.id, "0101"]
            channels = [Interaction.channel.id]*2
            shards = [self.singularitybot.shard_id,self.singularitybot.shard_id]
            names = [user.discord.display_name,ennemy_data["name"]]
            match_request = create_fight_handler_request(players,channels,shards,names)
            match_request["IA_DATA"] = ennemy_data
            winner,combat_log = await wait_for_fight_end(self.singularitybot.database,match_request)
            if not winner.is_human:
                # The Person has lost
                break
        for character in user.main_characters:
            character.xp += int(CHARACTER_XPGAINS * (tower["levels"] + 1 / (i + 1)))
        user.xp += int(PLAYER_XPGAINS * (tower["levels"] + 1 / (i + 1)))
        tower["rewards"].sort(key=lambda x: x["p"], reverse=True)
        # What happens when you gain no items
        if tower["unlocks"][i] == 0:
            embed = disnake.Embed(
                title="You did not go far enough to claim rewards", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=TOWERURL)
            await user.update()
            await Interaction.channel.send(embed=embed)
            return
        reward_items = [
            {"id": i["id"]} for i in tower["rewards"][0 : tower["unlocks"][i]]
        ]
        #I did this in STFU no idea what this does but it works
        probabilities = [i["p"] for i in tower["rewards"][0 : tower["unlocks"][i]]]
        sum_level = (i * (i + 1)) / 2
        probabilities_ndrop = [(7 - n) / sum_level for n in range(1, i + 1)]
        number_of_drops = random.choices(
            list(range(1, i + 1)), probabilities_ndrop, k=1
        )[0]
        items = random.choices(reward_items, probabilities, k=number_of_drops)

        items = [item_from_dict(get_item_from_template(item)) for item in items]
        title = "Tower"

        if i + 1 == tower["levels"] and winner.is_human:
            # the tower is completed
            title = "You have completed this tower ! You can go onto the next one. If it is available"
            embed = disnake.Embed(title=title, color=disnake.Color.dark_purple())
            embed.add_field(
                name="REWARDS",
                value="    ▬▬▬▬▬▬▬▬▬\n",
                inline=False,
            )
            if user.tower_level <= tower_id:
                user.tower_level = tower_id + 1
                first_item = item_from_dict(tower["first_completion_reward"])
                embed.add_field(
                    name="🎊 First Completion reward 🎊",
                    value=f"{first_item.name}|{first_item.emoji}",
                    inline=False,
                )
                items.append(first_item)
        else:
            title = "You failed to complete the tower"
            embed = disnake.Embed(title=title, color=disnake.Color.dark_purple())
            embed.add_field(
                name="Rewards",
                value="    ▬▬▬▬▬▬▬▬▬\n",
                inline=False,
            )

        for item in items:
            embed.add_field(name=f"{item.name}", value=f"{item.emoji}", inline=False)
            user.items.append(item)
        #await user.update()
        embed.set_image(url=TOWERURL)
        await Interaction.channel.send(embed=embed)

    @commands.slash_command(
        name="test", description="Enter towers to farm items and stands !"
    )
    @database_check()
    async def test(self, Interaction: disnake.ApplicationCommandInteraction):
        for i in range(1, 9):
            file = await tower_images["1"](Interaction.author, i)
            embed = disnake.Embed(color=disnake.Color.blue())
            embed.set_image(file=file)
            await Interaction.send(embed=embed)


def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Tower(singularitybot))