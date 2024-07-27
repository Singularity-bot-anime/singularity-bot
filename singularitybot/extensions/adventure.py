import disnake
import datetime
import random
from disnake.ext import commands

from singularitybot.utils.decorators import energy_check,database_check
from singularitybot.globals.variables import DONOR_ADV_WAIT_TIME,NORMAL_ADV_WAIT_TIME
from singularitybot.globals.emojis import CustomEmoji
from singularitybot.utils.functions import secondsToText
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.items import get_item_from_template,item_from_dict
from singularitybot.ui.paginator import Menu 

class Adventure(commands.Cog):
    """Adventure commands"""

    def __init__(self, bot: SingularityBot):
        self.singularitybot = bot

    @commands.slash_command(
        name="adventure",
        description="Embark on an the main adventure!",
    )
    async def adventure(self, Interaction: disnake.ApplicationCommandInteraction):
        pass  # This will handle the main command

    @adventure.sub_command(
        name="begin",
        description="Begin your adventure!",
    )
    async def begin(self, Interaction: disnake.ApplicationCommandInteraction):
        # page 1
        embed1 = disnake.Embed(color=disnake.Color.dark_purple())
        embed1.set_image(url="https://media.singularityapp.online/images/quests/begin/1.jpg")
        # page 2
        embed2 = disnake.Embed(color=disnake.Color.dark_purple())
        embed2.set_image(url="https://media.singularityapp.online/images/quests/begin/2.jpg")
        # page 3
        embed3 = disnake.Embed(color=disnake.Color.dark_purple())
        embed3.set_image(url="https://media.singularityapp.online/images/quests/begin/3.jpg")
        # page 4
        embed4 = disnake.Embed(color=disnake.Color.dark_purple())
        embed4.set_image(url="https://media.singularityapp.online/images/quests/begin/4.jpg")
        # page 5
        embed5 = disnake.Embed(color=disnake.Color.dark_purple())
        embed5.set_image(url="https://media.singularityapp.online/images/quests/begin/5.jpg")

        # add user 
        await self.singularitybot.database.add_user(Interaction.author.id)
        # add a sfrag
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        
        user.super_fragements += 1
        
        await user.update()

        await Interaction.response.send_message(embed=embed1,view=Menu([embed1, embed2,embed3,embed4,embed5]))

        embed=disnake.Embed(title="Welcome to the singularity", description="This give you the basic commands and mechanics of the bot, if you want to see this again use `/adventure tutorial` use `/profile` to see your status", color=disnake.Color.dark_purple())
        embed.add_field(name="Get new characters ✨", value="Summoning new character require super fragments, use `/banner view` to see the current active banners. And use `/banner pull [name of the banner]` to pull a new character", inline=True)
        embed.add_field(name="Repeatable pve 🧟", value="Some pve commands can be used every so often, use `/wormehole` to face random ennemies based on your level. Towers are based of anime or banners. They are a trial of endurance. The Higher you go in the tower the better the rewards use `/tower` to acces one", inline=True)
        embed.add_field(name="Manage your characters 📦", value="Managing your team is essential to win. use the `/character` command to manage your characters, `/items` to manage items", inline=True)
        embed.add_field(name="Team up 👥", value="The bot has a ''Clan'' system called galaxies, create or join one using `/galaxy create` or `/galaxy join` you will gain acces to new rewards and Galaxy wars !", inline=True)
        embed.set_footer(text="Good luck !")

        await Interaction.channel.send(embed=embed)
    

    @adventure.sub_command(
        name="tutorial",
        description="Get a tutorial on how to play the bot!",
    )
    async def tutorial(self, Interaction: disnake.ApplicationCommandInteraction):
        embed=disnake.Embed(title="Welcome to the singularity", description="This give you the basic commands and mechanics of the bot, if you want to see this again use `/adventure tutorial` use `/profile` to see your status", color=disnake.Color.dark_purple())
        embed.add_field(name="Get new characters ✨", value="Summoning new character require super fragments, use `/banner view` to see the current active banners. And use `/banner pull [name of the banner]` to pull a new character", inline=True)
        embed.add_field(name="Repeatable pve 🧟", value="Some pve commands can be used every so often, use `/wormehole` to face random ennemies based on your level. Towers are based of anime or banners. They are a trial of endurance. The Higher you go in the tower the better the rewards use `/tower` to acces one", inline=True)
        embed.add_field(name="Manage your characters 📦", value="Managing your team is essential to win. use the `/character` command to manage your characters, `/items` to manage items", inline=True)
        embed.add_field(name="Team up 👥", value="The bot has a ''Clan'' system called galaxies, create or join one using `/galaxy create` or `/galaxy join` you will gain acces to new rewards and Galaxy wars !", inline=True)
        embed.set_footer(text="Good luck !")
    
        await Interaction.send(embed=embed)

    @adventure.sub_command(
        name="daily",
        description="Claim your daily rewards!",
    )
    @database_check()
    async def daily(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        past_time = user.last_adventure
        now = datetime.datetime.now() + datetime.timedelta(hours=2)

        delta = now - past_time
        wait_time = DONOR_ADV_WAIT_TIME + (not user.is_donator()) * NORMAL_ADV_WAIT_TIME

        if delta.total_seconds() // 3600 < wait_time:
            wait_for = (
                datetime.timedelta(hours=wait_time) - delta
                if datetime.timedelta(hours=wait_time) > delta
                else delta - datetime.timedelta(hours=wait_time)
            )
            embed = disnake.Embed(
                title="You still need to wait to use this command",
                description="You can use {} in {}".format(
                    "/adventure daily", secondsToText(wait_for.total_seconds())
                ),
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url="https://media.singularityapp.online/images/assets/pfpsister.png")
            await Interaction.send(embed=embed)
            return
        user.last_adventure = now
        roll = random.randint(1, 100)
        bonus_fragments = 100
        embed = disnake.Embed(color=disnake.Color.dark_purple())
        embed.set_image(url="https://media.singularityapp.online/images/assets/pfpsister.png")

        if roll < 101:
            embed.add_field(
                name="You have won some fragments", value=f"`{bonus_fragments}` {CustomEmoji.FRAGMENTS}"
            )
            user.fragments += bonus_fragments
        if roll < 10:
            id = random.choice([1, 2, 3])
            item = item_from_dict(get_item_from_template({"id": id}))
            embed.add_field(
                name="You have won an item", value=f"`{item.name}`|{item.emoji}"
            )
            user.items.append(item)
        if roll < 5:
            embed.add_field(
                name="You have won ...", value=f" `1` {CustomEmoji.SUPER_FRAGMENTS}"
            )
            user.super_fragements += 1
        await        Interaction.send(embed=embed)
        await user.update()
    @adventure.sub_command(
        name="move",
        description="Move to a new location!"
    )
    async def move(self, interaction: disnake.ApplicationCommandInteraction):
        view = MoveView(self.map_instance)
        await interaction.response.send_message("Choose a direction to move:", view=view)
def setup(bot: SingularityBot):
    bot.add_cog(Adventure(bot))
