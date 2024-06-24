import disnake
from disnake.ext import commands
from disnake import TextInputStyle

# Subclassing the modal.
class ShopModal(disnake.ui.Modal):
    def __init__(self):
        self.name: str = "Create your shop",
        self.description: str = "your shop (We are not responsible for whatever you put here)"
        # The details of the modal, and its components
        components = [
            disnake.ui.TextInput(
                label="Shop Name",
                placeholder="Enter shop name...",
                custom_id="shop_name",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Shop Description",
                placeholder="Enter shop description...",
                custom_id="shop_description",
                style=TextInputStyle.paragraph,
            ),
        ]
        super().__init__(
            title="Create Shop",
            custom_id="create_shop",
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(title="Shop Created")
        embed.set_image(url="https://storage.singularityapp.online/randomAsset/shop.gif")
        for key, value in inter.text_values.items():
            embed.add_field(
                name=key.capitalize(),
                value=value,
                inline=False,
            )
        await inter.response.send_message(embed=embed)
