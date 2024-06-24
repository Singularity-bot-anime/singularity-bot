import disnake
from disnake.ext import commands
from disnake import TextInputStyle

# Subclassing the modal.
class GalaxyModal(disnake.ui.Modal):
    def __init__(self):
        # The details of the modal, and its components
        components = [
            disnake.ui.TextInput(
                label="Galaxy Name",
                placeholder="Enter galaxy name...",
                custom_id="galaxy_name",
                style=TextInputStyle.short,
                max_length=25,
            ),
            disnake.ui.TextInput(
                label="Galaxy MOTD",
                placeholder="Enter galaxy MOTD...",
                custom_id="galaxy_motd",
                style=TextInputStyle.paragraph,
            ),
            disnake.ui.TextInput(
                label="Galaxy Motto",
                placeholder="Enter galaxy motto...",
                custom_id="galaxy_motto",
                style=TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(
            title="Create Galaxy",
            custom_id="create_galaxy",
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(
            title="Galaxy Created", color=disnake.Color.blue()
        )
        embed.set_image(
            url="https://storage.singularityapp.online/randomAsset/galaxy_default.jpg"
        )
        for key, value in inter.text_values.items():
            embed.add_field(
                name=key.capitalize(),
                value=value,
                inline=False,
            )
        await inter.response.send_message(embed=embed)
