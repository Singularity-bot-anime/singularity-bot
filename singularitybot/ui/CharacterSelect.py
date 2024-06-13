import disnake
import json

from singularitybot.globals.emojis import CustomEmoji,converter
from singularitybot.models.gameobjects.character import Character
from typing import List, Union

# drop downelement class character_list
class Dropdown(disnake.ui.Select):
    def __init__(
        self,
        character_list: List[Character],
        disabled: List[bool],
        lang: str = "en",
        max_value: int = 1,
        min_value: int = 1,
    ):
        self.character_list = character_list
        self.lang = lang
        self.stop = False
        self.max_value = max_value
        if len(disabled) == 0:
            disabled = [False] * len(character_list)
        options = [
            disnake.SelectOption(
                label=f"『{character.name}』",
                description=f'level :{character.level} n°{index+1}',
                emoji=converter[character.rarity],
                value=str(index),
            )
            for index, character in enumerate(character_list)
            if not disabled[index]
        ]
        super().__init__(
            placeholder="Select the Character",
            min_values=min_value,
            max_values=max_value,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # get the Character index
        index = int(self.values[0])
        v: CharacterSelectDropdown = self.view
        # get the message initial content

        view = disnake.ui.View()
        view.add_item(
            disnake.ui.Button(
                label=f"You have selected 『{self.character_list[index].name}』",
                disabled=True,
                style=disnake.ButtonStyle.blurple,
                emoji=converter[self.character_list[index].rarity],
            )
        )
        self.interaction = interaction
        await interaction.response.edit_message(view=view)
        if self.max_value == 1:
            v.value = int(self.values[0])
        else:
            v.value = [int(i) for i in self.values]
        v.stop()


class CharacterSelectDropdown(disnake.ui.View):
    def __init__(
        self,
        interaction: disnake.Interaction,
        character_list: List[Character],
        disabled: List[bool] = [],
        lang: str = "en",
        timeout: float = 180,
        max_value: int = 1,
        min_value: int = 1,
        custom_user: disnake.User = None,
    ):
        super().__init__()
        self.value: Union[List[int], int] = None
        self.timeout = timeout
        self.interaction = interaction
        self.custom_user = custom_user
        # Adds the dropdown to our view object.
        self.add_item(
            Dropdown(
                character_list,
                disabled,
                lang=lang,
                max_value=max_value,
                min_value=min_value,
            )
        )

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # check if the author is the one who pressed the
        return (
            self.interaction.author.id == interaction.author.id
            and self.custom_user == None
        ) or self.custom_user.id == interaction.author.id