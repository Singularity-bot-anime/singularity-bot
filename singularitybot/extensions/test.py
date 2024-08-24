import disnake
from disnake.ext import commands

import os

# singularity model
from singularitybot.models.bot.singularitybot import SingularityBot

from typing import List

class Tests(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot
    

    @commands.slash_command(name="skus", description="get skus")
    async def get_skus(self,Interaction):
        await Interaction.send(self.singularitybot.skus())

def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Tests(singularitybot))