import disnake
import asyncio
import datetime

from typing import List, Union
from discord.ext import commands

from singularitybot.models.database.maindatabase import Database
from singularitybot.globals.variables import LOOP
from singularitybot.models.gameobjects.galaxy import GalaxyRank


def energy_check():
    """
    Check if the user has enough energy to use the command. Replenishes energy if more than 24 hours have passed.
    Displays an error message if they don't have enough energy after replenishment.
    """
    database = Database(LOOP)

    async def check(Interaction: disnake.ApplicationCommandInteraction) -> bool:
        if not Interaction.response.is_done():
            await Interaction.response.defer()
        
        if not await database.user_in_database(Interaction.author.id):
            embed = disnake.Embed()
            disnake.Color.dark_purple()
            embed.set_image(url="https://media.singularityapp.online/images/assets/notregistered.jpg")
            await Interaction.send(embed=embed)
            return False
        user = await database.get_user_info(Interaction.author.id)

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)

        # Check if 24 hours have passed since last energy replenishment
        if (now - user.last_full_energy).total_seconds() >= 24 * 60 * 60 and user.energy < user.total_energy:
            user.energy = user.total_energy  # Replenish energy
            user.last_full_energy = now
            await user.update()

        if user.energy < 1:
            embed = disnake.Embed(
                title="Not enough energy",
                description="You need at least 1 energy to use this command.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return False

        user.energy -= 1
        await user.update()
        return True

    return commands.check(check)

def database_check():
    """check for the existence of data about the context author
        display an error message otherwise

        if this decorator is above a command database.get_userInfo can be
        used without fear of returning None
    Args:
        slash_command:wether it's a slash command check or not

    Returns:
        [type]: [return a check decorator]
    """
    database = Database(LOOP)

    async def check(Interaction: disnake.ApplicationCommandInteraction) -> bool:
        """
            inner check
        Args:
            ctx (commands.Context): disnake Context

        Returns:
            bool: the anwser
        """
        """
        if await database.isBanned(Interaction.author.id):
            embed = disnake.Embed(
                title="It seems like you've been permanently banned from the bot.",
                description="Contact us via our website if you would like to get more infos.",
                color=0xFF0000,
            )
            await Interaction.send(embed=embed)
            return False
        """
        if not(Interaction.response.is_done()):
            await Interaction.response.defer()
        if not await database.user_in_database(Interaction.author.id):
            embed = disnake.Embed(color=disnake.Color.dark_purple())
            embed.set_image(url="https://media.singularityapp.online/images/assets/notregistered.jpg")
            await Interaction.send(embed=embed)
            return False
        return True

    return commands.check(check)

def shop_check():
    database = Database(LOOP)

    async def check(Interaction: disnake.ApplicationCommandInteraction) -> bool:
        user = await database.get_user_info(Interaction.author.id)
        # Shop does no exists
        if user.shop_id == None:
            embed = disnake.Embed(
                title="You have no created a shop",
                color=disnake.Color.red(),
            )
            embed.set_image(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            await Interaction.send(embed=embed)
            return False
        return True

    return commands.check(check)

def galaxy_check():
    database = Database(LOOP)

    async def check(Interaction: disnake.ApplicationCommandInteraction) -> bool:
        user = await database.get_user_info(Interaction.author.id)
        translation = await database.get_interaction_lang(Interaction)
        # gang does no exists
        if user.galaxy_id == None:
            embed = disnake.Embed(
                title="You are not a part of a gang",
                color=disnake.Color.red(),
            )
            embed.set_image(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            await Interaction.send(embed=embed)
            return False
        return True

    return commands.check(check)


def galaxy_rank_check(minimum_rank: GalaxyRank = GalaxyRank.STARDUST):
    """ Checks whether the user as a sufficient rank in their Galaxy to use the command
    can be used to replace `Galaxy_check`

    Args:
        minimum_rank (GalaxyRank, optional): rank to use the command Defaults to GalaxyRank.SOLDIER.
    """
    database = Database(LOOP)

    async def check(Interaction: disnake.ApplicationCommandInteraction) -> bool:
        user = await database.get_user_info(Interaction.author.id)

        # gang does no exists
        if user.galaxy_id == None:
            embed = disnake.Embed(
                title="You are not a part of a gang",
                color=disnake.Color.red(),
            )
            embed.set_image(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            await Interaction.send(embed=embed)

            return False

        galaxy = await database.get_galaxy_info(user.gang_id)
        rank = galaxy.ranks[user.id]
        return rank <= minimum_rank

    return commands.check(check)

def inner_permissions(type: str = "give_character"):
    """Allow to check if a user is allowed to use a command based on our own perssion levels
    Args:
        type (str, optional): can be `developer`, `give_character` or `tester`. Defaults to `tester`.

    Returns:
        [type]: [description]
    """
    developers = [
        242367586233352193,  # EIRBLAST
        112866272106012672,  # Arkkos
        289413979644755970,  # Kelian
    ]
    testers = developers + [
        248492672979959809,  # EIRBOT
        435082104381112340,  # Allways
    ]
    give_character = developers + [
        704961055662538833,  # Keyshiwo
        348342650853785602,  # Greg
        476057912532533273,  # Pickle
        435082104381112340,  # Allways
    ]

    async def check(Interaction: disnake.ApplicationCommandInteraction) -> bool:
        if type == "developer" and not Interaction.author.id in developers:
            embed = disnake.Embed(
                title="An error has occurred",
                description="This command is developer only",
                color=disnake.Colour.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            await Interaction.send(embed=embed)
            return False
        if type == "tester" and not Interaction.author.id in testers:
            embed = disnake.Embed(
                title="An error has occurred",
                description="This command is testers only",
                color=disnake.Colour.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            await Interaction.send(embed=embed)
            return False
        if type == "give_character" and not Interaction.author.id in give_character:
            embed = disnake.Embed(
                title="An error has occurred",
                description="This command is at least moderator only",
                color=disnake.Colour.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            await Interaction.send(embed=embed)
            return False
        return True

    return commands.check(check)
