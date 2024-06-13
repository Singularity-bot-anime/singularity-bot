import disnake

from singularitybot.models.database.user import User
from singularitybot.models.gameobjects.character import Character
from singularitybot.globals.emojis import CustomEmoji
from singularitybot.ui.place_holder import PlaceHolder

from typing import List, Union

EmojiList = [
    CustomEmoji.ONE,
    CustomEmoji.TWO,
    CustomEmoji.THREE,
    "🏳️",
]


class FightButton(disnake.ui.Button):
    def __init__(self, postion: int):
        super().__init__(
            style=disnake.ButtonStyle.secondary,
            emoji=EmojiList[postion],
            custom_id=str(postion),
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        view: FightUi = self.view
        view.value = int(self.custom_id)
        view.interaction = interaction
        await view.interaction.response.edit_message(view=PlaceHolder())
        view.stop()


class FightButtonFF(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            style=disnake.ButtonStyle.red, emoji=EmojiList[3], custom_id="ff"
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        view: FightUi = self.view
        view.value = self.custom_id
        view.interaction = interaction
        await view.interaction.response.edit_message(view=PlaceHolder())
        view.stop()


# Define a simple View that gives us a confirmation menu
class FightUi(disnake.ui.View):
    def __init__(
        self,

        user_id: int,
        watcher_characters: List[Character],
        player_characters: List[Character],
    ):
        super().__init__(timeout=60.0)  # 1 min timeout
        self.value = None
        self.user_id=user_id
        # add the coresponding button to the view
        for i in range(len(watcher_characters)):
            # check if a button should be added
            if watcher_characters[i].is_alive():
                self.add_item(FightButton(i))
        # add the forfeit button
        self.add_item(FightButtonFF())

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # check if the author is the one who pressed the
        return self.user_id == interaction.author.id