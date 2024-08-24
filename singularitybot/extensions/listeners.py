import disnake
import os
from disnake.ext import commands


# singularity model
from singularitybot.models.bot.singularitybot import SingularityBot

from typing import List

class Listeners(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.Cog.listener()
    async def on_entitlement_update(self, entitelement):
        pass
    
    @commands.Cog.listener()
    async def on_entitlement_delete(self, entitelement):
        pass

    @commands.Cog.listener()
    async def on_entitlement_create(self, entitelement):
        pass
    

def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Listeners(singularitybot))