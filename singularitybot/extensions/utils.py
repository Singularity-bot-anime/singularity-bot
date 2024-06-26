import disnake
import datetime
from disnake.ext import commands
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.utils.functions import secondsToText
from singularitybot.utils.image_generators import get_profile_image
from singularitybot.utils.decorators import database_check
from singularitybot.globals.variables import (
    DONOR_WH_WAIT_TIME,
    NORMAL_WH_WAIT_TIME,
    DONOR_ADV_WAIT_TIME,
    NORMAL_ADV_WAIT_TIME,
)
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
    
        profile_image_file = await get_profile_image(user,self.singularitybot)
        
        await Interaction.send(file=profile_image_file)
    @commands.slash_command(name="cooldowns", description="Show a cooldown list")
    @database_check()
    async def cooldowns(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)

        # Get the current time and user last times
        now = datetime.datetime.now()
        times = {
            "energy recharge":(user.last_full_energy,24,24),
            "Adventure": (user.last_adventure, DONOR_ADV_WAIT_TIME, NORMAL_ADV_WAIT_TIME),
            "Vote": (user.last_vote, 12, 12),
            "Wormhole": (user.last_wormhole, DONOR_WH_WAIT_TIME, NORMAL_WH_WAIT_TIME),
            "Advert": (user.last_advert, 6, 6),
        }

        def calculate_status(last_time, donor_wait, normal_wait):
            wait_time = donor_wait if user.is_donator() else normal_wait
            delta = now - last_time
            if delta.total_seconds() / 3600 <= wait_time:
                wait_for = datetime.timedelta(hours=wait_time) - delta
                return f"🕛 {secondsToText(wait_for.total_seconds())} left"
            return "✅ ready"

        # Calculate statuses
        statuses = {key: calculate_status(*value) for key, value in times.items()}

        # Create the embed
        embed = disnake.Embed(title="Your cooldowns:", color=disnake.Colour.dark_purple())
        embed.set_thumbnail(url="https://cdn.iconscout.com/icon/free/png-256/clock-1605637-1360989.png")

        if not user.is_donator():
            embed.add_field(
                name="Want lower cooldown? Consider donating",
                value="Use the /donate command for more information",
            )
        for key, status in statuses.items():
            embed.add_field(name=f"{key} cooldown:", value=status, inline=False)

        # Add buttons to the view if cooldowns are over
        view = disnake.ui.View()
        links = {
            "Advert link": ("Advert", "https://stfurequiem.com/ads"),
            "Vote link": ("Vote", "https://stfurequiem.com/vote"),
        }
        for label, (key, url) in links.items():
            if (now - times[key][0]).total_seconds() // 3600 > times[key][1]:
                view.add_item(disnake.ui.Button(label=label, style=disnake.ButtonStyle.url, url=url))

        await Interaction.send(embed=embed, view=view if view.children else None)


    @commands.slash_command(
        name="donate", description="show information about donation"
    )
    async def donate(self, Interaction: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Donation",
            url="https://patreon.com/EIRBLAST",
            description="Donate to support the team and get cool loot !",
            color=disnake.Colour.blue(),
        )
        embed.set_footer(
            text="Donate only if you can, and if you really want to support us!"
        )
        embed.add_field(name="Link:", value="https://patreon.com/EIRBLAST", inline=True)
        await Interaction.send(embed=embed)


def setup(client: SingularityBot):
    client.add_cog(Utils(client))