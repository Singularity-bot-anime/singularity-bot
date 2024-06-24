import disnake

from singularitybot.globals.variables import SHOPCREATIONCOST, ITEMTYPE, ITEMBYTYPE
from singularitybot.globals.emojis import CustomEmoji

# utils
from singularitybot.utils.decorators import database_check, shop_check
from singularitybot.utils.functions import wait_for, is_url_image

# singularitybot model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.shop import Shop
from singularitybot.models.gameobjects.items import item_from_dict

# specific class import
from disnake.ext import commands
from typing import List

# ui
from singularitybot.ui.shop.shop_creation_prompt import ShopModal
from singularitybot.ui.shop.item_select_shop import ShopItemSelectDropdown
from singularitybot.ui.place_holder import PlaceHolder
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.item_select import ItemSelectDropdown


async def autocomplete_type(inter, string: str) -> List[str]:
    return [lang for lang in ITEMTYPE if string.lower() in lang.lower()]


class Shop(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.slash_command(
        name="shop", description="Every command to manage and buy at shops"
    )
    @database_check()
    async def shop(self, Interaction: disnake.ApplicationCommandInteraction):
        pass

    @shop.sub_command(name="create", description="Create a public shop.")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def create(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        # Shop already exists
        if user.shop_id != None:
            embed = disnake.Embed(
                title="You already have a shop, leave it to create a new one.",
                color=disnake.Color.red(),
            )
            embed.set_image(url=self.singularitybot.avatar_url)
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title=f"You need to pay {SHOPCREATIONCOST} fragments to create a new shop.",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url="https://storage.singularityapp.online/randomAsset/shop.gif")
        view = Confirm(Interaction)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        Interaction = view.interaction

        # Refuse to pay the price
        if not view.value:
            embed = disnake.Embed(
                title="You can create a shop anytime.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url="https://storage.singularityapp.online/randomAsset/shop.gif")
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return
        user.fragments -= SHOPCREATIONCOST
        modal = ShopModal()
        await Interaction.response.send_modal(modal=modal)

        modal_inter: disnake.ModalInteraction = await self.singularitybot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_shop"
            and i.author.id == Interaction.author.id,
            timeout=300,
        )
        shop_name = modal_inter.text_values["shop_name"]
        shop_description = modal_inter.text_values["shop_description"]
        id = await self.singularitybot.database.add_shop(shop_name, shop_description, user.id)
        user.shop_id = id
        await user.update()

    @shop.sub_command(name="sell", description="Sell an item to your shop")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @shop_check()
    async def sell(
        self, Interaction: disnake.ApplicationCommandInteraction
    ):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        shop = await self.singularitybot.database.get_shop_info(user.shop_id)

        if len(shop.items) >= 24:
            embed = disnake.Embed(title="Your shop is full. Remove items to add more.")
            embed.set_image(url=shop.image_url)
            await Interaction.send(embed=embed)
            return
        if len(user.items) <= 0:
            embed = disnake.Embed(title="You have no item to sell")
            embed.set_image(url=shop.image_url)
            await Interaction.send(embed=embed)
            return
        embed = disnake.Embed(title="Select an item to sell in your shop.")
        embed.set_image(url=shop.image_url)
        view = ItemSelectDropdown(Interaction, user.items)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        index = view.value
        item = user.items.pop(index)
        price = item.price  # Assuming intrinsic_value is the sell price

        shop.sell(item, price)
        await shop.update()
        await user.update()
        embed = disnake.Embed(
            title=f"{item.name} has been added to your shop for {price} fragments."
        )
        embed.set_image(url=shop.image_url)
        await Interaction.channel.send(embed=embed)

    @shop.sub_command(name="remove", description="Remove an item from your shop")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @shop_check()
    async def remove(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        shop = await self.singularitybot.database.get_shop_info(user.shop_id)

        if len(shop.items) == 0:
            embed = disnake.Embed(
                title="Your shop is empty.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=shop.image_url)
            await Interaction.send(embed=embed)
            return

        view = ShopItemSelectDropdown(Interaction, shop.items, shop.prices)
        embed = disnake.Embed(
            title="Select an item to remove from your shop.",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=shop.image_url)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)

        item = shop.items.pop(view.value)
        price = shop.prices.pop(view.value)
        user.items.append(item)

        await shop.update()
        await user.update()

        embed = disnake.Embed(
            title=f"{item.name} has been removed from your shop.",
            color=disnake.Color.dark_purple(),
        )
        await Interaction.channel.send(embed=embed)

    @shop.sub_command(name="show", description="Show your own shop")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @shop_check()
    async def show(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        shop = await self.singularitybot.database.get_shop_info(user.shop_id)
        embed = disnake.Embed(
            title=f"{user.discord.name}'s Shop",
            color=disnake.Color.dark_purple(),
        )
        embed.add_field(
            name=shop.name,
            value=shop.description,
            inline=False,
        )
        embed.add_field(
            name="Items for Sale:",
            value="\n           ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            inline=False,
        )
        for i, item in enumerate(shop.items):
            embed.add_field(
                name=f"{item.name}{item.emoji}",
                value=f"Price: {shop.prices[i]} fragments",
                inline=True,
            )

        embed.set_image(url=shop.image_url)
        await Interaction.send(embed=embed)

    @shop.sub_command(name="changeimage", description="Change the shop image")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @shop_check()
    async def changeimage(
        self, Interaction: disnake.ApplicationCommandInteraction, url: str
    ):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        if not is_url_image(url):
            embed = disnake.Embed(
                title="URL Error",
                description="Please add a valid URL.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return

        shop = await self.singularitybot.database.get_shop_info(user.shop_id)

        shop.image_url = url
        await shop.update()
        embed = disnake.Embed(
            title="Your shop's image was changed.",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=shop.image_url)
        await Interaction.send(embed=embed)

    @shop.sub_command(
        name="buy", description="Buy the cheapest items from other players"
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def buy(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        itemtype: str = commands.Param(autocomplete=autocomplete_type),
    ):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        item_list = [item_from_dict(item) for item in ITEMBYTYPE[itemtype]]

        view = ItemSelectDropdown(Interaction, item_list)
        embed = disnake.Embed(
            title="Select an item to buy.",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url="https://storage.singularityapp.online/randomAsset/shop.gif")
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)

        item = item_list[view.value]

        shop, index = await self.singularitybot.database.find_suitable_shop(item, user.shop_id)

        if shop is None:
            embed = disnake.Embed(
                title="No suitable shop found.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url="https://storage.singularityapp.online/randomAsset/shop.gif")
            await Interaction.channel.send(embed=embed)
            return

        shop_item = shop.items[index]
        shop_price = shop.prices[index]

        if user.fragments < shop_price:
            embed = disnake.Embed(
                title="You don't have enough fragments.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url="https://storage.singularityapp.online/randomAsset/shop.gif")
            await Interaction.channel.send(embed=embed)
            return

        embed = disnake.Embed(title=shop.name, description=shop.description)
        embed.set_image(url=shop.image_url)
        embed.add_field(
            name="Item for Sale",
            value=f"{shop_item.name} for {shop_price} fragments.",
        )
        view = Confirm(Interaction)
        await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        Interaction = view.interaction
        if not view.value:
            embed = disnake.Embed(title=shop.name, description=shop.description)
            embed.set_image(url=shop.image_url)
            embed.add_field(
                name="Purchase Canceled",
                value="You did not purchase the item.",
            )
            await Interaction.send(embed=embed)
            return
        await shop.buy(index, user)
        embed = disnake.Embed(title=shop.name, description=shop.description)
        embed.set_image(url=shop.image_url)
        embed.add_field(
            name="Purchase Successful",
            value=f"You bought {shop_item.name}.",
        )
        await Interaction.send(embed=embed)


def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Shop(singularitybot))
