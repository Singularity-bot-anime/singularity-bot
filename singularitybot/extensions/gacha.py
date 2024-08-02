import disnake
from disnake.ext import commands
import json
import random
import asyncio
from singularitybot.utils.decorators import database_check
from singularitybot.utils.functions import wait_for,add_to_available_storage
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.database.user import User
from singularitybot.ui.paginator import Menu
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.place_holder import PlaceHolder
from singularitybot.models.gameobjects.character import Character, character_from_dict,get_character_from_template, Types, Qualities
from singularitybot.globals.emojis import CustomEmoji,converter

banners_test = ["banners1","banners2","banners3"]

with open('singularitybot/data/banners/banners_data.json', 'r') as f:
    BANNERS = json.load(f)["banners"]

async def pull_autocomplete(inter,banner_name:str)->list[str]:
    banner_name = banner_name.lower()
    return [banner["name"] for banner in BANNERS if (banner["enabled"] and banner_name in banner_name.lower())]

class Banners(commands.Cog):
    """Banner commands"""

    def __init__(self, bot: SingularityBot):
        self.singularitybot = bot
        with open('singularitybot/data/banners/banners_data.json', 'r') as f:
            BANNERS = json.load(f)["banners"]

    @commands.slash_command(
        name="banner",
        description="View available banners and pull cards!",
    )
    @database_check()
    async def banner(self, Interaction: disnake.ApplicationCommandInteraction):
        pass  # This will handle the main command

    @banner.sub_command(
        name="view",
        description="View all active banners!",
    )
    
    async def view(self, Interaction: disnake.ApplicationCommandInteraction):
        enabled_banners = [banner for banner in BANNERS if banner["enabled"]]

        user:User = await self.singularitybot.database.get_user_info(Interaction.author.id)

        if not enabled_banners:
            await Interaction.send("There are no active banners at the moment.")
            return

        # Create embeds for each banner
        banner_embeds = []
        for banner in enabled_banners:
            embed = disnake.Embed(
                title=banner["name"],
                description=f"Draw odds | {CustomEmoji.R_R}:80% {CustomEmoji.R_SR}:19% {CustomEmoji.R_SSR}:0.9% {CustomEmoji.R_UR}:0.1% | cost: {banner['cost']}{CustomEmoji.SUPER_FRAGMENTS}| pity:{user.pity}/100",
                color=disnake.Color.dark_purple()
            )
            embed.set_image(url=f"https://media.singularityapp.online/images/banners/banner_{banner['id']}.jpg")

            character_list = []
            for ids in banner["cards"]:
                character = get_character_from_template(self.singularitybot.character_file[ids - 1], [], [])
                character_list.append(f"{character.name}: {converter[character.rarity]}")

            # Group characters into fields of up to 1024 characters
            current_field_content = ""
            for character_info in character_list:
                if len(current_field_content) + len(character_info) + 1 > 1024:
                    embed.add_field(name="▬▬▬▬▬▬▬▬▬", value=current_field_content, inline=True)
                    current_field_content = character_info + "\n"
                else:
                    current_field_content += character_info + "\n"

            # Add any remaining characters to a final field
            if current_field_content:
                embed.add_field(name="▬▬▬▬▬▬▬▬▬", value=current_field_content, inline=True)

            banner_embeds.append(embed)

        if len(banner_embeds) == 1:
            await Interaction.send(embed=banner_embeds[0])
        else:
            await Interaction.send(embed=banner_embeds[0], view=Menu(banner_embeds))
    
    
    

    @banner.sub_command(
        name="pull",
        description="Pull 10 cards from an active banner!",
        
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def pull(self, Interaction: disnake.ApplicationCommandInteraction,banner_name:str=commands.Param(autocomplete=pull_autocomplete)):
        #reload
        user:User = await self.singularitybot.database.get_user_info(Interaction.author.id)
        banner = {}
        for _ in BANNERS:
            if _["name"] == banner_name:
                banner = _
                break

        if (banner['cost'] > user.super_fragements):
            embed = disnake.Embed(title=f"You don't have enoug{CustomEmoji.SUPER_FRAGMENTS}, the banner cost {banner['cost']} {CustomEmoji.SUPER_FRAGMENTS} you have {user.super_fragements}{CustomEmoji.SUPER_FRAGMENTS} ",color=disnake.Color.purple())
            await Interaction.send(embed=embed)
            return

        view = Confirm(Interaction)
        embed = disnake.Embed(title=f"Are you sure you want to use {banner['cost']} {CustomEmoji.SUPER_FRAGMENTS} you have {user.super_fragements}{CustomEmoji.SUPER_FRAGMENTS} ",
                                description=f"Pity {user.pity}/100 | You gain a 50% {CustomEmoji.R_UR} at 100",
                                color=disnake.Color.dark_purple())
        embed.set_image(url=f"https://media.singularityapp.online/images/banners/banner_{banner['id']}.jpg")
        
        await Interaction.send(embed=embed,view=view)
        await wait_for(view)

        Interaction = view.interaction
        if not view.value:
            await Interaction.response.edit_message(view=PlaceHolder())            
            return
        
        user.super_fragements -= 1
        drawn_characters = []
        pulled_rarities=[]
        draw_embed = disnake.Embed(title="Drawn Characters",color=disnake.Color.dark_purple())
        for _ in range(10):
            char_template,types,qualities = self.generate_character_data(banner,user)
            character = get_character_from_template(char_template,types, qualities)
            typequal = ""
            for _t,_q in zip(character.etypes,character.equalities):
                typequal+=f"{_t.emoji} {_q.emoji}\n"
            draw_embed.add_field(name=f"{character.name}{converter[character.rarity]}",value=typequal)
            msg = add_to_available_storage(user,character,skip_main=True)
            pulled_rarities.append(character.rarity)
            if not msg:
                embed = disnake.Embed(title=f"Your character storage is full ! you need at least 10 free slots",color=disnake.Color.dark_purple())
                await Interaction.send(embed=embed)
                return
                
            user.pity += 1
        await Interaction.response.defer()
        await user.update()
        pulled_rarities.sort(key=rarity_prio)
        embed = disnake.Embed(color=disnake.Color.dark_purple())
        embed.set_image(url=f"https://media.singularityapp.online/images/animations/{pulled_rarities[0]}.png")
        await Interaction.send(embed=embed)
        await asyncio.sleep(4)
        await Interaction.send(embed=draw_embed)

    def generate_character_data(self,banner:dict,user:User):
        #get types and qualities
        _types = [Types.ATTACK,Types.DEFENSE,Types.BALANCE,Types.LUCK,Types.SPEED]
        _qualities = [Qualities.UNIVERSAL,Qualities.SUPREME,Qualities.GREAT,Qualities.GOOD,Qualities.SUB_PAR,Qualities.BAD]
        _bad_qualities = [Qualities.SUB_PAR,Qualities.BAD]
        standard_probabilities = [0.05, 0.10, 0.20, 0.50, 0.10, 0.05]
        enhanced_probabilities = [0.40, 0.30, 0.20, 0.10, 0.05, 0.03]
        
        #we get at least 1 quality
        pulled_types = [random.choice(_types)]
        remove_i = _types.index(pulled_types[-1])
        standard_probabilities.pop(remove_i)
        enhanced_probabilities.pop(remove_i)
        _types.pop(remove_i)
        pulled_qualities = [random.choice(_qualities)]
        _qualities.pop(remove_i)
        pull_prob = 0.1
        #We get a second pull if the first one is bad with better odds
        #We remove the quality we just pulled to not draw them again
        if pulled_qualities[-1] in _bad_qualities:
            pull_prob = 1
        while(random.random() <= pull_prob and len(_types) >0):
            weights = standard_probabilities
            if pulled_qualities[-1] in _qualities:
                weights = enhanced_probabilities
            pulled_types.append(random.choice(_types))
            pulled_qualities.append(random.choices(_qualities,weights=weights,k=1)[0])
            remove_i = _types.index(pulled_types[-1])
            standard_probabilities.pop(remove_i)
            enhanced_probabilities.pop(remove_i)
            _types.pop(remove_i)
            _qualities.pop(remove_i)
            pull_prob = 0.1
        
        #we pull now a character
        #pity system
        if user.pity >= 100:
            user.pity = 0
            rarity = random.choice(["UR","SSR"])
        else:
            _rarities = ["R","SR","SSR","UR"]
            weights = [0.8,0.19,0.009,0.001]
            rarity = random.choices(_rarities,weights=weights,k=1)[0]
        character_template = random.choice([self.singularitybot.character_file[char-1] for char in banner["cards"] if self.singularitybot.character_file[char-1]["rarity"] == rarity])
        
        #we convert the type and qualities to strings
        pulled_types = [_t.name for _t in pulled_types]
        pulled_qualities = [_q.name for _q in pulled_qualities]
        return character_template,pulled_types,pulled_qualities
        

def rarity_prio(rarity):
    i = ["R","SR","SSR","UR","LR"].index(rarity)
    return [4,3,2,1,0][i]



def setup(bot: SingularityBot):
    bot.add_cog(Banners(bot))