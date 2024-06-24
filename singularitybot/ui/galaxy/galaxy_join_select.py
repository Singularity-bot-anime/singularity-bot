import disnake

from typing import List

from singularitybot.models.gameobjects.galaxy import Galaxy

# drop down element class
class Dropdown(disnake.ui.Select):
    def __init__(
        self,
        galaxies: List[Galaxy],
        lang: str = "en",
    ):
        self.galaxies = galaxies
        self.lang = lang
        options = [
            disnake.SelectOption(
                label=f"{galaxy.name}",
                emoji="🏡",
                value=i,
            )
            for i, galaxy in enumerate(galaxies)
        ]
        super().__init__(
            placeholder="Select a galaxy",
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # get the stand index
        index = int(self.values[0])
        v: GalaxySelectDropdown = self.view
        # get the message initial content

        view = disnake.ui.View()
        view.add_item(
            disnake.ui.Button(
                label=f"You have selected {self.galaxies[index].name}",
                disabled=True,
                style=disnake.ButtonStyle.blurple,
                emoji="✅",
            )
        )
        self.interaction = interaction
        await interaction.response.edit_message(view=view)
        v.value = index
        v.stop()


class GalaxySelectDropdown(disnake.ui.View):
    def __init__(
        self,
        interaction: disnake.Interaction,
        galaxies: List[Galaxy],
        lang: str = "en",
        timeout: float = 180,
    ):
        super().__init__(timeout=timeout)
        self.value: int = None
        self.interaction = interaction
        # Adds the dropdown to our view object.
        self.add_item(Dropdown(galaxies, lang=lang))

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # check if the author is the one who pressed the
        return self.interaction.author.id == interaction.author.id
