from typing import List, Union
import disnake


# Define a simple View that gives us a confirmation menu
class Cancel(disnake.ui.View):
    def __init__(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        user: Union[disnake.User, None] = None,
        timeout: float = 180,
    ):
        super().__init__(timeout=timeout)
        self.value = None
        self.interaction = interaction
        self.user = user
        self.author = None

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # check if the author is the one who pressed the
        return (
            self.interaction.author.id == interaction.author.id and self.user == None
        ) or (self.user.id == interaction.author.id)

    # This one is similar to the confirmation button except sets the inner value to `False`
    @disnake.ui.button(label="Cancel",emoji="❌", style=disnake.ButtonStyle.blurple)
    async def cancel(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.value = True

        self.interaction = interaction
        self.author = interaction.author
        self.stop()
