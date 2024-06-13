import disnake
import random

from disnake.ext import commands
from typing import List

# ui
from singularitybot.ui.CharacterSelect import CharacterSelectDropdown
from singularitybot.ui.item_select import ItemSelectDropdown

# utils
from singularitybot.utils.decorators import database_check
from singularitybot.utils.functions import (
    wait_for,
    get_drop_from_list,
    character_field,
    add_to_available_storage,
)

# stfu model
from singularitybot.models.gameobjects.items import Item
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.character import Character, get_character_from_template


class Items(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.slash_command(name="item", description="manage item")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @database_check()
    async def item(self, Interaction: disnake.ApplicationCommandInteraction):
        pass

    @item.sub_command(
        name="inventory", description="show all your items in your inventory"
    )
    async def inventory(self, Interaction: disnake.ApplicationCommandInteraction):
        # translation
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        unique: List[Item] = []
        for item in user.items:
            if not item.id in [i.id for i in unique]:
                unique.append(item)

        embed = disnake.Embed(
            title="{}'s inventory".format(user.discord.name),
            color=disnake.Color.dark_purple(),
        )
        for item in unique:
            num = f" x{[i.id for i in user.items].count(item.id)}"
            embed.add_field(name=item.name + num, value=item.emoji, inline=False)
        await Interaction.send(embed=embed)

    @item.sub_command(name="equip", description="equip an item on a character")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def equip(self, Interaction: disnake.ApplicationCommandInteraction):
        # translation
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        if len(user.items) == 0:
            embed = disnake.Embed(
                title="You have no item to equip", color=disnake.Color.dark_purple()
            )
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title="Select an item to equip", color=disnake.Color.dark_purple()
        )
        view = CharacterSelectDropdown(Interaction, user.main_characters)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character_index = view.value
        character: Character = user.main_characters[character_index]

        if len(character.items) == 3:
            embed = disnake.Embed(
                title="This character already as `3` item equiped use /item unequip ot /item unequipall", color=disnake.Color.dark_purple()
            )
            await Interaction.channel.send(embed=embed)
            return

        embed = disnake.Embed(
            title="select an item to equip", color=disnake.Color.dark_purple()
        )
        equipable = [i for i in user.items if i.is_equipable]
        if len(equipable) == 0:
            embed = disnake.Embed(
                title="You have no equipable item", color=disnake.Color.dark_purple()
            )
            await Interaction.channel.send(embed=embed)
            return
        view = ItemSelectDropdown(Interaction, equipable)
        await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        item = equipable.pop(view.value)
        user.items.remove(item)
        user.main_characters[character_index].items.append(item)

        embed = disnake.Embed(
            title="{} was equiped on {}".format(item.name, character.name),
            color=disnake.Color.dark_purple(),
        )
        await user.update()
        await Interaction.channel.send(embed=embed)

    @item.sub_command(name="unequip", description="unequip an item")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def unequip(self, Interaction: disnake.ApplicationCommandInteraction):
        # translation
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        embed = disnake.Embed(
            "Choose a character to unequip an item from", color=disnake.Color.dark_purple()
        )
        view = CharacterSelectDropdown(Interaction, user.main_characters)
        
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character_index = view.value
        character: Character = user.main_characters[character_index]

        if len(character.items) == 0:
            embed = disnake.Embed(
                title="This character has no items to unequip", color=disnake.Color.dark_purple()
            )
            await Interaction.channel.send(embed=embed)
            return

        view = ItemSelectDropdown(Interaction, character.items)
        await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        item = character.items.pop(view.value)
        user.main_characters[character_index] = character
        user.items.append(item)
        embed = disnake.Embed(
            title="{} was unequiped from {}".format(item.name, character.name),
            color=disnake.Color.dark_purple(),
        )
        await user.update()
        await Interaction.channel.send(embed=embed)

    @item.sub_command(name="unequipall", description="unequip all items from a character")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def unequip_all(self, Interaction: disnake.ApplicationCommandInteraction):
        # translation
        translation = await self.singularitybot.database.get_interaction_lang(Interaction)
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        embed = disnake.Embed(
            "Choose a character to unequip an item from", color=disnake.Color.dark_purple()
        )
        view = CharacterSelectDropdown(Interaction, user.main_characters)
        
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character_index = view.value
        character: Character = user.main_characters[character_index]

        if len(character.items) == 0:
            embed = disnake.Embed(
                title="This character has no items to unequip", color=disnake.Color.dark_purple()
            )
            await Interaction.channel.send(embed=embed)
            return

        for item in character.items:
            user.items.append(item)
        character.items = []
        user.main_characters[character_index] = character
        embed = disnake.Embed(
            title="All items where unequiped from {}".format(character.name),
            color=disnake.Color.dark_purple(),
        )
        await user.update()
        await Interaction.channel.send(embed=embed)

    """@item.sub_command(name="use", description="use one of your non equipable items.")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def use(self, Interaction: disnake.ApplicationCommandInteraction):
        translation = await self.singularitybot.database.get_interaction_lang(Interaction)
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        usable_items = [item for item in user.items if not item.is_equipable]
        if len(usable_items) == 0:
            embed = disnake.Embed(
                title=translation["use"]["1"], color=disnake.Color.blue()
            )
            embed.set_image(url=self.singularitybot.avatar_url)
            await Interaction.send(embed=embed)
            return
        embed = disnake.Embed(title=translation["use"]["2"], color=disnake.Color.blue())
        view = ItemSelectDropdown(Interaction, usable_items)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        index = view.value
        item = usable_items[index]
        index = [i.id for i in user.items].index(item.id)
        item = user.items.pop(index)

        # Gacha items
        gacha_item = [2, 12]
        # Stand chip
        chip_ids = [
            8,
            9,
            10,
            11,
            14,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
        ]
        actual_id = [
            9,
            0,
            5,
            29,
            162,
            30,
            57,
            31,
            33,
            44,
            48,
            49,
            58,
            59,
            68,
            74,
            77,
            79,
            80,
            82,
            83,
        ]
        # Requiem IDs
        requiemable = [49, 6, 59]
        requiem_stand = [57, 82, 83]
        # stand to excluse from gacha
        special_stand = [163, 110, 84, 109, 161, 120, 114]
        # action based on which item was used
        if item.id in gacha_item:  # Stand arrows classic gacha
            if item.id == 2:

                stand_list = [
                    get_stand_from_template(stand)
                    for stand in self.singularitybot.stand_file
                    if not stand["id"] in special_stand
                ]
            if item.id == 12:
                stand_list = [
                    get_stand_from_template(stand)
                    for stand in self.singularitybot.stand_file
                    if stand["id"] < 31 and not stand["id"] in special_stand
                ]
            drop: Stand = get_drop_from_list(stand_list)[0]
            msg = add_to_available_storage(user, drop)
            if msg:
                embed = disnake.Embed(
                    title=translation["use"]["3"].format(msg),
                    color=disnake.Color.blue(),
                )
                embed.set_thumbnail(
                    url="https://vignette.wikia.nocookie.net/jjba/images/9/9f/Arrow_anime.png/revision/latest?cb=20190614222010"
                )
                embed = stand_fields(drop, embed)
                await user.update()
                await Interaction.channel.send(embed=embed)
                return
            embed = disnake.Embed(
                title=translation["use"]["4"], color=disnake.Color.blue()
            )
            embed.set_image(url=self.singularitybot.avatar_url)
            await Interaction.channel.send(embed=embed)
            return
        if item.id == 3:  # Requiem stand
            view = StandSelectDropdown(Interaction, user.stands)
            embed = disnake.Embed(
                title=translation["use"]["5"], color=disnake.Color.blue()
            )
            await Interaction.channel.send(embed=embed, view=view)
            await wait_for(view)
            stand: Stand = user.stands[view.value]
            if stand.ascension + stand.stars >= 7:
                embed = disnake.Embed(
                    title=translation["use"]["6"], color=disnake.Color.blue()
                )
                embed.set_image(url=self.singularitybot.avatar_url)
                await Interaction.channel.send(embed=embed)
                return
            if stand.id in requiemable and stand.ascension >= 2 and stand.level >= 100:
                index = requiemable.index(stand.id)
                new_stand_template = self.singularitybot.stand_file[requiem_stand[index]]
                new_stand = get_stand_from_template(new_stand_template)
                new_stand.items = stand.items
                new_stand.reset()
                user.stands[view.value] = new_stand
                await user.update()
                embed = disnake.Embed(
                    title=translation["use"]["7"], color=disnake.Color.blue()
                )
                embed = stand_fields(new_stand, embed)
                await Interaction.channel.send(embed=embed)
                return
            stand.ascension += 1
            user.stands[view.value] = stand
            embed = disnake.Embed(
                title=translation["use"]["8"].format(stand.name, stand.ascension),
                color=disnake.Color.blue(),
            )
            embed.set_image(url="https://storage.stfurequiem.com/item_special/6.gif")
            await user.update()
            await Interaction.channel.send(embed=embed)
        if item.id in chip_ids:  # Stand Chips
            index = chip_ids.index(item.id)
            new_stand_template = self.singularitybot.stand_file[actual_id[index]]
            new_stand = get_stand_from_template(new_stand_template)
            msg = add_to_available_storage(user, new_stand)
            if msg:
                embed = disnake.Embed(
                    title=translation["use"]["3"].format(msg),
                    color=disnake.Color.blue(),
                )
                embed = stand_fields(new_stand, embed)
                await user.update()
                await Interaction.channel.send(embed=embed)
                return
            embed = disnake.Embed(
                title=translation["use"]["4"], color=disnake.Color.blue()
            )
            await Interaction.channel.send(embed=embed)
            user.items.append(item)
            return
        if item.id == 13:  # bag of coins
            amount = random.randint(75, 125)
            user.coins += amount
            embed = disnake.Embed(
                title=translation["use"]["9"].format(amount), color=disnake.Color.blue()
            )
            embed.set_image(
                url="https://i.pinimg.com/originals/a5/e8/2d/a5e82d700ff336637489b44f32d36095.gif"
            )
            await user.update()
            await Interaction.channel.send(embed=embed)
            return"""


def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Items(singularitybot))