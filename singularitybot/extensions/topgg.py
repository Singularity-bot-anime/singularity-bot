import disnake
import topgg
import os
import datetime
import asyncio

from disnake.ext import commands, tasks

# globals
from singularitybot.globals.variables import ARROW_VOTE, COINS_VOTE
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

    def __init__(self, singularitybot: singularitybot):
        self.singularitybot = SingularityBot
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
    """
    @commands.slash_command(name="vote", description="vote to gain rewards !")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @database_check()
    async def vote(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        translation = await self.singularitybot.database.get_interaction_lang(Interaction)

        past_time = user.last_vote
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        Delta = now - past_time
        wait_time = 12
        if Delta.total_seconds() // 3600 <= wait_time:
            wait_for = (
                datetime.timedelta(hours=wait_time) - Delta
                if datetime.timedelta(hours=wait_time) > Delta
                else Delta - datetime.timedelta(hours=wait_time)
            )
            embed = disnake.Embed(
                title=translation["error_meesages"]["error"],
                description=translation["error_meesages"]["cool_down"].format(
                    "vote", secondsToText(wait_for.total_seconds())
                ),
                color=disnake.Colour.dark_purple(),
            )
            embed.set_thumbnail(
                url="https://cdn1.iconfinder.com/data/icons/finance-banking-and-currency-part-1/400/finance_2-512.png"
            )
            await Interaction.send(embed=embed)
            return
        embed = disnake.Embed(
            title=translation["vote"]["1"], color=disnake.Colour.dark_purple()
        )
        embed.add_field(
            name=translation["vote"]["2"].format(CustomEmoji.LOADING_ICON),
            value=translation["vote"]["3"],
        )
        embed.set_image(url=self.singularitybot.avatar_url)
        await Interaction.send(embed=embed)
        time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        while not await self.dblpy.get_user_vote(user.discord.id):
            delta = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)) - time
            if delta.total_seconds() > 5 * 60:
                raise TimeoutError
            await asyncio.sleep(10)
        user.last_vote = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        user.coins += COINS_VOTE
        user.items = user.items + [item_from_dict({"id": 2})] * ARROW_VOTE
        embed = disnake.Embed(
            title=translation["vote"]["4"], color=disnake.Colour.dark_purple()
        )
        embed.set_image(url=self.singularitybot.avatar_url)
        embed.add_field(name=f"`Arrows:`", value=f"{ARROW_VOTE}{CustomEmoji.ARROW}"),
        embed.add_field(name=f"`Coins`:", value=f"{COINS_VOTE}{CustomEmoji.COIN}")

        try:
            await self.post_to_stfurequiem_server(user)
        except:
            pass  # We don't log because it's not necessary !

        await user.update()
        await Interaction.delete_original_message()
        await Interaction.channel.send(embed=embed)

    async def post_to_stfurequiem_server(self, user: User):
        post_channel = await self.singularitybot.fetch_channel(990668989074141244)
        embed = disnake.Embed(
            title=f"🎊 {user.discord.display_name} has just voted 🗳️ on: https://top.gg/bot/715184823144153090 🎊 (Thank you !)",
            color=disnake.Colour.green(),
        )
        embed.set_thumbnail(url=user.discord.display_avatar.url)
        await post_channel.send(embed=embed)
    """

def setup(singularitybot: singularitybot):
    singularitybot.add_cog(TopGG(singularitybot))