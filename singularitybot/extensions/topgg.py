import disnake
import topgg
import os
import datetime
import asyncio

from disnake.ext import commands, tasks

# globals
from singularitybot.globals.variables import SUPERFRAGMENT_VOTE, COINS_VOTE
from singularitybot.globals.emojis import CustomEmoji

# utils
from singularitybot.utils.decorators import database_check
from singularitybot.utils.functions import secondsToText

# stfu model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.items import item_from_dict
from singularitybot.models.database.user import User


class TopGG(commands.Cog):
    """
    This example uses tasks provided by discord.ext to create a task that posts guild count to top.gg every 30 minutes.
    """

    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot
        self.token = os.environ["TOPGG"]  # set this to your DBL token
        self.dblpy = topgg.DBLClient(self.singularitybot, self.token)
        self.update_stats.start()
    
    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        await self.singularitybot.wait_until_ready()
        try:
            server_count = len(self.singularitybot.guilds)
            await self.dblpy.post_guild_count(server_count)
            print("Posted server count ({})".format(server_count))
        except Exception as e:
            print("Failed to post server count\n{}: {}".format(type(e).__name__, e))
    
    @commands.slash_command(name="vote", description="Vote to gain rewards!")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @database_check()
    async def vote(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        past_time = user.last_vote
        now = datetime.datetime.now() + datetime.timedelta(hours=2)
        Delta = now - past_time
        wait_time = 12

        if Delta.total_seconds() // 3600 <= wait_time:
            wait_for = (
                datetime.timedelta(hours=wait_time) - Delta
                if datetime.timedelta(hours=wait_time) > Delta
                else Delta - datetime.timedelta(hours=wait_time)
            )
            embed = disnake.Embed(
                title="Error",
                description=f"You need to wait {secondsToText(wait_for.total_seconds())} before you can vote again.",
                color=disnake.Colour.dark_purple(),
            )
            embed.set_thumbnail(
                url="https://cdn1.iconfinder.com/data/icons/finance-banking-and-currency-part-1/400/finance_2-512.png"
            )
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title="Vote for Rewards!",
            color=disnake.Colour.dark_purple(),
        )
        embed.add_field(
            name=f"Voting... {CustomEmoji.LOADING_ICON}",
            value="Please wait while we check your vote status.",
        )
        embed.set_image(url=self.singularitybot.avatar_url)
        
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label="Vote!", style=disnake.ButtonStyle.url, url="https://top.gg/bot/1086877089543753748/vote"))
        await Interaction.send(embed=embed,view=view)

        time = datetime.datetime.now() + datetime.timedelta(hours=2)
        while not await self.dblpy.get_user_vote(user.discord.id):
            delta = (datetime.datetime.now() + datetime.timedelta(hours=2)) - time
            if delta.total_seconds() > 5 * 60:
                raise TimeoutError
            await asyncio.sleep(10)

        user.last_vote = datetime.datetime.now() + datetime.timedelta(hours=2)
        user.fragments += COINS_VOTE
        user.super_fragements += SUPERFRAGMENT_VOTE

        embed = disnake.Embed(
            title="Thank you for voting!",
            color=disnake.Colour.dark_purple(),
        )
        embed.set_image(url=self.singularitybot.avatar_url)
        embed.add_field(name="super fragments:", value=f"{SUPERFRAGMENT_VOTE} {CustomEmoji.SUPER_FRAGMENTS}", inline=True)
        embed.add_field(name="fragments", value=f"{COINS_VOTE} {CustomEmoji.FRAGMENTS}", inline=True)

        await user.update()
        await Interaction.delete_original_message()
        await Interaction.channel.send(embed=embed)
    """
    async def post_to_stfurequiem_server(self, user: User):
        post_channel = await self.singularitybot.fetch_channel(990668989074141244)
        embed = disnake.Embed(
            title=f"🎊 {user.discord.display_name} has just voted 🗳️ on: https://top.gg/bot/715184823144153090 🎊 (Thank you !)",
            color=disnake.Colour.green(),
        )
        embed.set_thumbnail(url=user.discord.display_avatar.url)
        await post_channel.send(embed=embed)
    """

def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(TopGG(singularitybot))