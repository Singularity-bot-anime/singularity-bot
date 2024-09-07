import disnake
import json
from datetime import datetime, timedelta

from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.character import get_character_from_template
from singularitybot.models.gameobjects.items import item_from_dict

from singularitybot.utils.functions import add_to_available_storage, character_field
from singularitybot.utils.decorators import inner_permissions

from singularitybot.globals.emojis import CustomEmoji

from disnake.ext import commands
from typing import List
from enum import Enum


class awards(int, Enum):
    donor = 1
    FirstEggChampion = 2
    SecondEggChampion = 3
    ThirdEggChampion = 4
    ModTeam = 5
    StfuTeam = 6


"""
# For future discord permissions system
DEVELOPERS_PERMS = {}
for devs in DEVELOPER:
    DEVELOPERS_PERMS[f"{devs}"] = True
GIVESTAND_PERMS = {}
for gv in GIVESTAND:
    DEVELOPERS_PERMS[f"{gv}"] = True
TESTERS_PERMS = {}
for test in TESTERS:
    DEVELOPERS_PERMS[f"{test}"] = True
"""


class admincommands(commands.Cog):
    """all admin commands
    Args:
        commands ([type]): [description]
    """

    def __init__(self, bot: SingularityBot):
        self.SingularityBot = bot

    @inner_permissions()
    @commands.slash_command(
        name="admincommands",
        description="reserved to admins",
    )
    async def admin(self, Interaction: disnake.ApplicationCommandInteraction):
        pass

    @admin.sub_command(
        name="givedonor", description="give donor status to someone for 1 month"
    )
    @commands.is_owner()
    async def giveDonor(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        someone: disnake.Member,
    ):
        time = datetime.now() + timedelta(weeks=4) + timedelta(hours=2)
        user = await self.SingularityBot.database.get_user_info(someone.id)
        user.discord = someone
        user.donor_status = time
        await user.update()
        embed = disnake.Embed(title=f"Gave donor status to {someone.display_name} ")
        embed.set_image(
            url="https://vignette.wikia.nocookie.net/jjba/images/d/d2/JoJos-Bizarre-Adventure-Speedwagon.jpg/revision/latest/scale-to-width-down/340?cb=20140406083728&path-prefix=fr"
        )
        await Interaction.send(embed=embed)

    @admin.sub_command(name="givecharacter", description="Give a character to someone")
    @inner_permissions(type="give_character")
    async def givecharacter(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        characterid: int,
        asc: int,
        level: int
    ):
        char_template = self.SingularityBot.character_file[characterid - 1]
        character = get_character_from_template(char_template, [], [])
        user = await self.SingularityBot.database.get_user_info(member.id)
        character.level = level
        character.awaken = asc
        msg = add_to_available_storage(user, character)

        if msg:
            embed = disnake.Embed(
                title="Your character was added to {}".format(msg),
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=f"https://media.singularityapp.online/images/cards/{character.id}.png")
            embed = character_field(character, embed)
            await user.update()
            await Interaction.channel.send(embed=embed)
            return
        embed = disnake.Embed(title="Your storages are full", color=disnake.Color.dark_purple())
        embed.set_image(url=self.SingularityBot.avatar_url)
        await Interaction.channel.send(embed=embed)
        return

    @admin.sub_command(name="giveitem", description="Give an item to someone")
    @inner_permissions(type="give_item")
    async def giveitem(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        itemid: int,
    ):
        item = item_from_dict({"id":itemid})
        user = await self.SingularityBot.database.get_user_info(member.id)
        user.items.append(item)
        await user.update()
        embed = disnake.Embed(
            title=f"Added item {item.name} {item.emoji} to {member.display_name}",
            color=disnake.Color.green(),
        )
        await Interaction.send(embed=embed)

    @admin.sub_command(name="givefragments", description="give fragments to someone")
    @inner_permissions(type="give_character")
    async def givefragments(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        amount: int,
    ):
        user = await self.SingularityBot.database.get_user_info(member.id)
        user.discord = member
        user.fragments += amount
        await user.update()
        embed = disnake.Embed(
            title=f"added {amount}{CustomEmoji.FRAGMENTS} to {user.discord.display_name}"
        )
        await Interaction.send(embed=embed)


    @admin.sub_command(name="givesuperfragments", description="give super fragments to someone")
    @inner_permissions(type="give_character")
    async def giveSuperFragments(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        amount: int,
    ):
        user = await self.SingularityBot.database.get_user_info(member.id)
        user.discord = member
        user.super_fragements += amount
        await user.update()
        embed = disnake.Embed(
            title=f"added {amount}{CustomEmoji.SUPER_FRAGMENTS} to {user.discord.display_name}"
        )
        await Interaction.send(embed=embed)
    
    @admin.sub_command(name="debug", description="debug command group")
    @inner_permissions(type="developer")
    async def debug(self, Interaction: disnake.ApplicationCommandInteraction):
        pass
    
    @debug.sub_command(name="copydata", description="copy a user data to self")
    async def copydata(self, Interaction: disnake.ApplicationCommandInteraction, user: disnake.User):
        User = await self.SingularityBot.database.get_user_info(user.id)
        User.discord = user
        
        target = await self.SingularityBot.database.get_user_info(Interaction.author.id)
        target.data = User.data
        await target.update()
    
    @debug.sub_command(name="printdata", description="print a user data")
    async def printdata(self, Interaction: disnake.ApplicationCommandInteraction, user: disnake.User):
        User = await self.SingularityBot.database.get_user_info(user.id)
        await Interaction.send(f"```{json.dumps(User.data)}```")
    


def setup(client: SingularityBot):
    client.add_cog(admincommands(client))