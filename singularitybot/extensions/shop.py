import disnake
from disnake.ext import commands
import json
from typing import List

from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.items import Item
from singularitybot.globals.emojis import converter,CustomEmoji

# Load the shop catalog from a JSON file (shop_items.json)
with open(
    "singularitybot/data/templates/items.json", "r", encoding="utf-8"
) as item:
    shop_items = json.load(item)["items"]

class Shop(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.slash_command(name="shop", description="Shop for items")
    async def shop(self, Interaction: disnake.ApplicationCommandInteraction):
        pass

    ### LOOKUP COMMAND ###
    @shop.sub_command(name="lookup", description="Lookup an item from the shop")
    async def lookup(self, Interaction: disnake.ApplicationCommandInteraction, item_name: str):
        item = next((i for i in shop_items if i["name"].lower() == item_name.lower()), None)
        
        if not item:
            await Interaction.send(f"Item `{item_name}` not found in the shop.", ephemeral=True)
            return

        # Build the item information
        embed = disnake.Embed(
            title=f"🔍 `{item['name']}`{item['emoji']}",
            description=f"**▬▬▬`STATS`▬▬▬**\n\n"
                        f"**HP Bonus**➥ {item['bonus_hp']}❤️\n"
                        f"**Damage Bonus**➥ {item['bonus_damage']}⚔️\n"
                        f"**Speed Bonus**➥ {item['bonus_speed']}💨\n"
                        f"**Critical Bonus**➥ {item['bonus_critical']}🍀\n"
                        f"**Armor Bonus**➥ {item['bonus_armor']}🛡️\n"
                        f"▬▬▬▬▬▬▬▬▬",
            color=disnake.Color.dark_purple()
        )
        embed.add_field(name="▬▬▬`Equipable`▬▬▬", value=str(item['is_equipable']), inline=True)
        embed.add_field(name="▬▬▬`Special`▬▬▬", value=item['special_image'], inline=False)
        embed.set_thumbnail(url=item['special_image'])

        await Interaction.send(embed=embed)

    @lookup.autocomplete("item_name")
    async def autocomplete_lookup(self, Interaction: disnake.ApplicationCommandInteraction, current: str):
        """Autocomplete to search for items."""
        return [item["name"] for item in shop_items if (current.lower() in item["name"].lower()) and item["prurchasable"]]

    ### BUY COMMAND ###
    @shop.sub_command(name="buy", description="Buy an item from the shop")
    async def buy(self, Interaction: disnake.ApplicationCommandInteraction, item_name: str):
        # Fetch the user and item data
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        item = next((i for i in shop_items if i["name"].lower() == item_name.lower()), None)

        if not item or not item["prurchasable"]:
            await Interaction.send(f"The item `{item_name}` is not purchasable.", ephemeral=True)
            return
        
        # Check if the user has enough fragments (assuming 'user.fragments' exists)
        item_price = item["price"]
        item_emoji = item["emoji"]
        if user.fragments < item_price:
            await Interaction.send(f"You don't have enough fragments to buy {item_name}{item_emoji}.", ephemeral=True)
            return

        # Deduct price and add item to user
        user.fragments -= item_price
        user.items.append(Item(item))
        await user.update()

        embed = disnake.Embed(
            title=f"Purchase Successful!",
            description=f"You bought {item['name']}{item_emoji} for {item_price} {CustomEmoji.FRAGMENTS}!",
            color=disnake.Color.green()
        )
        await Interaction.send(embed=embed)

    @buy.autocomplete("item_name")
    async def autocomplete_buy(self, Interaction: disnake.ApplicationCommandInteraction, current: str):
        """Autocomplete to search for purchasable items."""
        purchasable_items = [item["name"] for item in shop_items if item["prurchasable"]]
        return [item for item in purchasable_items if current.lower() in item.lower()]

    ### SELL COMMAND ###
    @shop.sub_command(name="sell", description="Sell an item from your inventory")
    async def sell(self, Interaction: disnake.ApplicationCommandInteraction, item_name: str):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        # Check if the user owns the item
        item = next((i for i in user.items if i.name.lower() == item_name.lower()), None)
        
        if not item:
            await Interaction.send(f"You don't own the item `{item_name}`.", ephemeral=True)
            return

        # Sell for 1/10th of its price
        sell_price = item.price // 10 if item.price else 0
        item_emoji = item["emoji"]
        if sell_price == 0:
            await Interaction.send(f"`{item.name}`{item_emoji} cannot be sold.", ephemeral=True)
            return

        # Remove the item and add fragments
        user.items.remove(item)
        user.fragments += sell_price
        await user.update()

        embed = disnake.Embed(
            title=f"Item Sold!",
            description=f"You sold {item.name}{item_emoji} for {sell_price}  {CustomEmoji.FRAGMENTS}!",
            color=disnake.Color.orange()
        )
        await Interaction.send(embed=embed)

    @sell.autocomplete("item_name")
    async def autocomplete_sell(self, Interaction: disnake.ApplicationCommandInteraction, current: str):
        """Autocomplete to search for items in the user's inventory."""
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user_items = [item.name for item in user.items]
        return [item for item in user_items if current.lower() in item.lower()]

# Setup function for the cog
def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Shop(singularitybot))
