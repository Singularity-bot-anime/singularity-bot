import disnake
import random
import json

from disnake.ext import commands
from typing import List

# ui
from singularitybot.ui.CharacterSelect import CharacterSelectDropdown
from singularitybot.ui.item_select import ItemSelectDropdown
from singularitybot.ui.confirmation import Confirm

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

with open("singularitybot/data/templates/recipes.json") as file:
    recipes = json.load(file)["recipes"]


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
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        embed = disnake.Embed(
            title="Choose a character to unequip an item from", color=disnake.Color.dark_purple()
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
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        embed = disnake.Embed(
            title="Choose a character to unequip an item from", color=disnake.Color.dark_purple()
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
    
    @item.sub_command(name="craft", description="Craft an item from a recipe")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @database_check()
    async def craft(self, Interaction: disnake.ApplicationCommandInteraction, recipe_name: str):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        recipe = next((r for r in recipes if r["name"].lower() == recipe_name.lower()), None)
        if not recipe:
            embed = disnake.Embed(
                title="Recipe not found.",
                color=disnake.Color.dark_purple(),
            )
            await Interaction.send(embed=embed, ephemeral=True)
            return

        missing_items = []
        for ingredient in recipe["ingredients"]:
            item_id, required_amount = ingredient
            user_items_count = sum(1 for item in user.items if item.id == item_id)
            if user_items_count < required_amount:
                missing_items.append((item_id, required_amount - user_items_count))

        if missing_items:
            embed = disnake.Embed(color=disnake.Color.dark_purple())
            for item_id, amount in missing_items:
                item = Item({"id": item_id})
                embed.add_field(name=f"Missing {item.name} x{amount}", value=item.emoji, inline=True)
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title="Confirm Crafting",
            description=f"Do you want to craft {recipe_name}?",
            color=disnake.Color.dark_purple(),
        )
        view = Confirm(Interaction)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)

        if not view.value:
            embed = disnake.Embed(
                title="Crafting Canceled",
                description="You have canceled the crafting process.",
                color=disnake.Color.dark_purple(),
            )
            await Interaction.send(embed=embed, ephemeral=True)
            return

        for ingredient in recipe["ingredients"]:
            item_id, required_amount = ingredient
            for _ in range(required_amount):
                item = next(item for item in user.items if item.id == item_id)
                user.items.remove(item)

        crafted_item = Item({"id":recipe["result"]})
        user.items.append(crafted_item)

        await user.update()

        embed = disnake.Embed(
            title="Crafting Successful",
            description=f"You have crafted {crafted_item.name}{crafted_item.emoji}.",
            color=disnake.Color.dark_purple(),
        )
        await Interaction.send(embed=embed)

    @craft.autocomplete("recipe_name")
    async def autocomplete_recipe_name(self, Interaction: disnake.ApplicationCommandInteraction, current: str):
        return [recipe["name"] for recipe in recipes if current.lower() in recipe["name"].lower()]

    @item.sub_command(name="use", description="Use an item from your inventory")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def use(self, Interaction: disnake.ApplicationCommandInteraction, item_name: str):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        # Find the item in the user's inventory
        item = next((i for i in user.items if i.name.lower() == item_name.lower()), None)
        
        if item is None:
            embed = disnake.Embed(
                title="Error",
                description="Item not found in your inventory.",
                color=disnake.Color.red()
            )
            await Interaction.send(embed=embed, ephemeral=True)
            return

        if not item.is_usable:
            embed = disnake.Embed(
                title="Item Unusable",
                description=f"{item.name} cannot be used.",
                color=disnake.Color.red()
            )
            await Interaction.send(embed=embed, ephemeral=True)
            return

        # Item usage logic
        if item.id == 22:
            # Add 10 energy to the user
            user.energy += 10
            user.items.remove(item)
            await user.update()  # Update user data in the database
            embed = disnake.Embed(
                title="Item Used",
                description=f"You used {item.name}{item.emoji} and gained 5 energy!",
                color=disnake.Color.green()
            )
        else:
            # General item usage logic (if any)
            embed = disnake.Embed(
                title="Item Used",
                description=f"You used {item.name}!",
                color=disnake.Color.green()
            )

        await Interaction.send(embed=embed, ephemeral=True)

    @use.autocomplete("item_name")
    async def autocomplete_use_item(self, Interaction: disnake.ApplicationCommandInteraction, current: str):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        usable_items = [item.name for item in user.items if item.is_usable]
        return [item for item in usable_items if current.lower() in item.lower()]
        
def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Items(singularitybot))