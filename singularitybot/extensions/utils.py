import disnake
from disnake.ext import commands
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.utils.image_generators import get_profile_image
from singularitybot.utils.decorators import database_check

class Utils(commands.Cog):
    """Utility commands"""

    def __init__(self, bot: SingularityBot):
        self.singularitybot = bot

    @commands.slash_command(
        name="profile",
        description="Display user profile",
    )
    @database_check()
    async def profile(self, Interaction: disnake.ApplicationCommandInteraction):
        #reload
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        profile_image_file = await get_profile_image(user)
        
        await Interaction.send(file=profile_image_file)

def setup(client: SingularityBot):
    client.add_cog(Utils(client))