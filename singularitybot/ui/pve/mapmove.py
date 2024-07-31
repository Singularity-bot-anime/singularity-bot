# SPDX-License-Identifier: MIT

import disnake
from typing import List, Optional


class MoveButton(disnake.ui.Button):
    def __init__(self, direction: str, row: int):
        # A label is required; here we use the direction name as the label.
        super().__init__(style=disnake.ButtonStyle.primary, label=direction.capitalize(), row=row)
        self.direction = direction

    # This method is called whenever this button is pressed.
    async def callback(self, interaction: disnake.MessageInteraction):
        view: MoveView = self.view  # Type hinting for view
        view.value = self.direction  # Store the direction chosen
        view.interaction = interaction
        view.stop()  # Stop the view from listening for more button presses


class MoveView(disnake.ui.View):
    def __init__(self,interaction, allowed_moves: List[str], timeout: Optional[float] = 180.0):
        super().__init__(timeout=timeout)
        self.value = None
        self.interaction = interaction
        # Dynamically create buttons based on allowed moves
        for direction in allowed_moves:
            self.add_item(MoveButton(direction, 0))

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # check if the author is the one who pressed the
        return self.interaction.author.id == interaction.author.id
