import disnake
import asyncio

from redis.asyncio import Redis
from disnake.ext import commands

#globl

from singularitybot.globals.emojis import CustomEmoji
# ui
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.paginator import Menu

# utils
from singularitybot.utils.functions import wait_for,create_ranked_fight_request,create_fight_handler_request,wait_for_fight_end,format_combat_log,wait_for_match,wait_for_ranked_stop
from singularitybot.utils.decorators import database_check,energy_check
from singularitybot.utils.image_generators import get_fight_image, get_win_image

# stfu model
from singularitybot.models.bot.singularitybot import SingularityBot

MATCHMAKING_QUEUE = "matchmaking_requests"

class fight(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot:disnake.AutoShardedClient = singularitybot
    
    @commands.slash_command(name="fight", description="fight someone in your server")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def fight(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
    ):
        pass


    @fight.sub_command(name="local", description="fight someone in your server")
    @database_check()
    async def local(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        ennemy: disnake.Member,
    ):
    
        if ennemy.id == Interaction.author.id:
            await Interaction.send("You cannot fight yourself!")
            return

        file_ = await get_fight_image(Interaction.author,ennemy)
        embed = disnake.Embed(color=disnake.Colour.dark_purple())
        embed.set_image(file=file_)
        
        # Check if the enemy is in the database
        if not await self.singularitybot.database.user_in_database(ennemy.id):
            embed.add_field(name="ERROR",value=f"{ennemy.display_name} is not in the database. They need to register first!")
            await Interaction.send(embed=embed)
            return
        
        user_1 = await self.singularitybot.database.get_user_info(ennemy.id)
        user_2 = await self.singularitybot.database.get_user_info(Interaction.author.id)

        if not user_2.main_characters or not user_1.main_characters:
            embed.add_field(name="ERROR",value=f"You need to have main characters to fight use `/character main`")
            await Interaction.send(embed=embed)
            return
        
        embed = disnake.Embed(title=f"{ennemy.display_name} do you want to fight {Interaction.author.display_name}",color=disnake.Colour.dark_purple())
        embed.set_image(file=file_)
        view = Confirm(Interaction,user=ennemy)
        await Interaction.send(embed=embed,view=view)
        await wait_for(view)
        await Interaction.delete_original_message()
        if not view.value:
            embed.add_field(name="Match canceled",value=f"{ennemy.display_name} refused to fight")
            await Interaction.channel.send(embed=embed)
            return

        # create the match trough the handler
        players = [Interaction.author.id,ennemy.id]
        channels = [Interaction.channel.id,Interaction.channel.id]
        shards = [self.singularitybot.shard_id,self.singularitybot.shard_id]
        names = [Interaction.author.display_name,ennemy.display_name]
        match_request = create_fight_handler_request(players,channels,shards,names)
        try:
            winner,combat_log = await asyncio.wait_for(wait_for_fight_end(self.singularitybot.database, match_request),timeout=600)
        except asyncio.TimeoutError:
            # If the fight times out after 10 minutes
            embed = disnake.Embed(
                title="Fight Timeout",
                description="The fight took too long and has been terminated.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return
        # cleanup & end
        # user_1.energy -= 1
        # user_2.energy -= 1

        await user_1.update()
        await user_2.update()
        winner = await self.singularitybot.fetch_user(int(winner.id))
        file_= await get_win_image(winner)
        win_embed = disnake.Embed(color=disnake.Colour.dark_purple())
        win_embed.set_image(file=file_)
        embeds = format_combat_log(combat_log)
        final_view = Menu(embeds)
        await Interaction.channel.send(embed=win_embed)
        await Interaction.channel.send(embed=embeds[0], view=final_view)

    
    @fight.sub_command(name="ranked", description="Start a ranked fight")
    @database_check()
    async def ranked(self, interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(interaction.author.id)

        if not user.main_characters:
            embed = disnake.Embed(title="You need to have main characters to fight use `/character main`",colour=disnake.Colour.dark_purple())
            embed.set_image(url=self.singularitybot.avatar_url)
            await interaction.send(embed=embed)
            return
        # Create matchmaking request
        match_request = create_ranked_fight_request(
            interaction.author.id,
            interaction.channel.id,
            self.singularitybot.shard_id,
            interaction.author.display_name,
            user.global_elo,  # Use global ELO for matchmaking
        )

        # Add to matchmaking queue
        await self.singularitybot.database.publish(MATCHMAKING_QUEUE, match_request)

        match_found = await wait_for_match(self.singularitybot.database, interaction)
        if not match_found:
            embed = disnake.Embed(title=f"Matchmaking Queue", description=f"You have left the queue", color=disnake.Color.dark_purple())
            embed.set_image(url="https://media1.tenor.com/m/2OA-uQTBCBQAAAAd/detective-conan-case-closed.gif")
            await interaction.edit_original_message(embed=embed,view=None)
            return
        
        winner,combat_log = await wait_for_ranked_stop(self.singularitybot.database,interaction.author.id)
        # cleanup & end    
        winner = await self.singularitybot.fetch_user(int(winner.id))
        file_= await get_win_image(winner)
        win_embed = disnake.Embed(color=disnake.Colour.dark_purple())
        win_embed.set_image(file=file_) 
        embeds = format_combat_log(combat_log)
        final_view = Menu(embeds)
        await interaction.channel.send(embed=win_embed)
        await interaction.channel.send(embed=embeds[0], view=final_view)
    

    @fight.sub_command(name="test", description="fight a target dummy")
    @database_check()
    async def test(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
    ):
        
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        if not   user.main_characters:
            embed = disnake.Embed(title=f"Test fight    ",color=disnake.Colour.dark_purple())
            embed.add_field(name="ERROR",value=f"You need to have main characters to fight use `/character main`")
            await Interaction.send(embed=embed)
            return

        await Interaction.delete_original_message()
        
        ennemy_data = {
            "name":"Dummy",
            "avatar": None,
            "main_characters": [
                { "id": 76, "xp": 100, "types":[],"qualities":[],"awaken": 0, "items": [{ "id": 5 }] }
            ],
        }
        players = [user.id, "0101"] 
        channels = [Interaction.channel.id]*2
        shards = [self.singularitybot.shard_id]*2
        names = [user.discord.display_name,ennemy_data["name"]]
        match_request = create_fight_handler_request(players,channels,shards,names)
        match_request["IA_DATA"] = ennemy_data
        try:
            winner,combat_log = await asyncio.wait_for(wait_for_fight_end(self.singularitybot.database, match_request),timeout=600)
        except asyncio.TimeoutError:
            # If the fight times out after 10 minutes
            embed = disnake.Embed(
                title="Fight Timeout",
                description="The fight took too long and has been terminated.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return
        
        embeds = format_combat_log(combat_log)
        final_view = Menu(embeds)
        await Interaction.channel.send(embed=embeds[0], view=final_view)


def setup(client: SingularityBot):
    client.add_cog(fight(client))