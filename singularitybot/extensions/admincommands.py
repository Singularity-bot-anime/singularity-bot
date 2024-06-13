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

    @commands.slash_command(
        name="emojis",
        description="Display all emojis and their IDs",
        guild_ids=[
            1097995244336848928,
            1086875022808854528,
        ],
    )
    @inner_permissions()
    async def emojis(self, Interaction: disnake.ApplicationCommandInteraction):
        # Create an embed to display emojis and IDs
        embed = disnake.Embed(title="Emoji IDs", color=disnake.Color.blue())
        
        # Add each emoji and its ID to the embed
        for emoji in Interaction.guild.emojis:
            embed.add_field(name=str(emoji), value=f"ID: {emoji.id}", inline=False)

        await Interaction.response.send_message(embed=embed)

    @inner_permissions()
    @commands.slash_command(
        name="admincommands",
        description="reserved to admins",
        guild_ids=[
            1097995244336848928,
            1086875022808854528,
        ],
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
        time = datetime.now() + timedelta(weeks=4)
        user = await self.SingularityBot.database.get_user_info(someone.id)
        user.discord = someone
        user.donor_status = time
        await user.update()
        embed = disnake.Embed(title=f"Gave donor status to {someone.display_name} ")
        embed.set_image(
            url="https://vignette.wikia.nocookie.net/jjba/images/d/d2/JoJos-Bizarre-Adventure-Speedwagon.jpg/revision/latest/scale-to-width-down/340?cb=20140406083728&path-prefix=fr"
        )
        await Interaction.send(embed=embed)

    @admin.sub_command(name="givecharacter", description="Give a stand to someone")
    @inner_permissions(type="give_character")
    async def givecharacter(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        standid: int,
        star: int,
    ):
        stand = self.SingularityBot.stand_file[standid - 1]
        stand = get_stand_from_template(stand)
        user = await self.SingularityBot.database.get_user_info(member.id)
        translation = await self.SingularityBot.database.get_interaction_lang(Interaction)
        msg = add_to_available_storage(user, stand)

        if msg:
            embed = disnake.Embed(
                title=translation["use"]["3"].format(msg),
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=f"https://storage.stfurequiem.com/Image/{stand.id}.png")
            embed = stand_fields(stand, embed)
            await user.update()
            await Interaction.channel.send(embed=embed)
            return
        embed = disnake.Embed(title=translation["use"]["4"], color=disnake.Color.dark_purple())
        embed.set_image(url=self.SingularityBot.avatar_url)
        await Interaction.channel.send(embed=embed)
        return

    @admin.sub_command(name="givefragments", description="give fragments to someone")
    @inner_permissions(type="give_character")
    async def giveCoin(
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
            title=f"added {amount}{CustomEmoji.COIN} to {user.discord.display_name}"
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
            title=f"added {amount}{CustomEmoji.COIN} to {user.discord.display_name}"
        )
        await Interaction.send(embed=embed)


    @admin.sub_command(name="giveoh", description="give OH status to someone")
    @commands.is_owner()
    async def giveOH(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        someone: disnake.Member,
    ):
        user = await self.SingularityBot.database.get_user_info(someone.id)
        user.discord = someone
        user.over_heaven_supporter = True
        embed = disnake.Embed(
            title=f"Gave OVER HEAVEN donor status to {someone.display_name}  THANKS for everything"
        )
        embed.set_image(
            url="https://c.tenor.com/5sahUGLcwbkAAAAd/dio-heaven-ascension-jjba.gif"
        )
        await Interaction.send(embed=embed)


def setup(client: SingularityBot):
    client.add_cog(admincommands(client))