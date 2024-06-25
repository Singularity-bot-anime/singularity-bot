import disnake
import random
import asyncio

# utils
from singularitybot.utils.decorators import database_check
from singularitybot.utils.functions import (
    play_files,
    sign,
    wait_for,
    add_to_available_storage,
    character_field
)


# character model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.models.gameobjects.character import Character

# specific class import
from disnake.ext import commands
from singularitybot.globals.emojis import converter,CustomEmoji
# ui
from singularitybot.ui.place_holder import PlaceHolder
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.CharacterSelect import CharacterSelectDropdown
from singularitybot.ui.storage.ChooseDonor import ChooseStorage


class management(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.slash_command(name="character", description="character management")
    @database_check()
    async def character(self, Interaction: disnake.ApplicationCommandInteraction):
        pass

    @character.sub_command(name="show", description="show one of your main character stats.")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def show(self, Interaction: disnake.ApplicationCommandInteraction):
        User = await self.singularitybot.database.get_user_info(Interaction.author.id)
        if User.main_characters == []:
            embed = disnake.Embed(color=disnake.Color.dark_purple())
            embed.set_image(url="https://media.singularityapp.online/images/assets/nomain.jpg")
            await Interaction.send(embed=embed, ephemeral=True)
        else:
            # make an embed
            embed = disnake.Embed(
                title="Which character would you like to select ?",
                color=disnake.Colour.purple(),
            )
            view = CharacterSelectDropdown(Interaction, User.main_characters)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)
            index = view.value
            # get the stand

            character: Character = User.main_characters[index]
            embed = disnake.Embed(color=disnake.Color.purple())
            embed = character_field(character,embed)
            await Interaction.channel.send(embed=embed)


    @character.sub_command(name="remove", description="Remove a character from your storage")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def remove(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        storage = user.character_storage
        premium = False
        if user.is_donator():
            embed = disnake.Embed(
                title="Choose a storage", color=disnake.Color.purple()
            )
            view = ChooseStorage(Interaction)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)
            Interaction = view.interaction
            if view.value:
                premium = True
                storage = user.pcharacter_storage

        if storage == []:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.purple(),
            )
            embed.set_image(url="https://media.singularityapp.online/images/assets/pfpsister.png")
            if Interaction.response.is_done():
                await Interaction.send(embed=embed, ephemeral=True)
                return
            await Interaction.channel.send(embed=embed, ephemeral=True)
            return
        embed = disnake.Embed(
            title=f"{user.discord.display_name} character's storage",
            color=disnake.Color.purple(),
        )
        for character in user.character_storage:
            typequal = ""
            for _t,_q in zip(character.etypes,character.equalities):
                typequal+=f"{_t.emoji} {_q.emoji}\n"
            embed.add_field(name=f"{character.name}{converter[character.rarity]}{int(character.level)}",value=typequal)
        
        view = CharacterSelectDropdown(Interaction, storage,max_value=len(storage))
        if Interaction.response.is_done():
            await Interaction.send(embed=embed, view=view)
        else:
            await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        storage = [storage[c] for c in range(len(storage)) if not c in view.value ]
        embed = disnake.Embed(
            title="Do you want to remove these characters ? They can't be retreived",
            color=disnake.Color.blue(),
        )
        for character in [user.character_storage[i] for i in range(len(user.character_storage)) if i in view.value ]:
            typequal = ""
            for _t,_q in zip(character.etypes,character.equalities):
                typequal+=f"{_t.emoji} {_q.emoji}\n"
            embed.add_field(name=f"{character.name}{converter[character.rarity]}{int(character.level)}",value=typequal)
        view = Confirm(Interaction)
        await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        Interaction = view.interaction
        if view.value:
            embed = disnake.Embed(
                title="The characters were removed",
                color=disnake.Color.purple(),
            )
            if premium:
                user.pcharacter_storage = storage
            else:
                user.character_storage = storage
            await user.update()
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return
        embed = disnake.Embed(
            title="The characters were not removed",
            color=disnake.Color.purple(),
        )
        await Interaction.response.edit_message(embed=embed, view=PlaceHolder(), ephemeral=True)

    @character.sub_command(name="storage", description="show your character storage")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def storage(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        storage = user.character_storage

        if user.is_donator():
            embed = disnake.Embed(
                title="Choose a storage", color=disnake.Color.purple()
            )
            view = ChooseStorage(Interaction)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)
            Interaction = view.interaction
            if view.value:
                storage = user.pcharacter_storage

        if storage == []:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.purple(),
            )
            embed.set_image(url="https://media.singularityapp.online/images/assets/pfpsister.png")
            if Interaction.response.is_done():
                await Interaction.send(embed=embed, ephemeral=True)
                return
            await Interaction.channel.send(embed=embed, ephemeral=True)
            return
        embed = disnake.Embed(
            title=f"{user.discord.display_name} character's storage",
            color=disnake.Color.purple(),
        )
        for character in user.character_storage:
            typequal = ""
            for _t,_q in zip(character.etypes,character.equalities):
                typequal+=f"{_t.emoji} {_q.emoji}\n"
            embed.add_field(name=f"{character.name}{converter[character.rarity]}",value=typequal)
        if Interaction.response.is_done():
            await Interaction.send(embed=embed)
            return
        await Interaction.channel.send(embed=embed)

    @character.sub_command(
        name="main", description="move a character from storage to your main character"
    )
    async def maincharacter(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        storage = user.character_storage
        premium = False
        if user.is_donator():
            embed = disnake.Embed(
                title="Choose a storage", color=disnake.Color.purple()
            )
            view = ChooseStorage(Interaction)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)
            Interaction = view.interaction
            if view.value:
                premium = True
                storage = user.pcharacter_storage

        if not storage:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.purple(),
            )
            embed.set_image(url="https://media.singularityapp.online/images/assets/pfpsister.png")
            if Interaction.response.is_done():
                await Interaction.send(embed=embed)
                return
            await Interaction.channel.send(embed=embed)
            return

        embed = disnake.Embed(
            title="Choose a character to make your main",
            color=disnake.Color.purple(),
        )
        for character in storage:
            typequal = ""
            for _t,_q in zip(character.etypes,character.equalities):
                typequal+=f"{_t.emoji} {_q.emoji}\n"
            embed.add_field(name=f"{character.name}{converter[character.rarity]}",value=typequal)
        view = CharacterSelectDropdown(Interaction, storage)
        if Interaction.response.is_done():
            await Interaction.send(embed=embed, view=view)
        else:
            await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        character = storage.pop(view.value)
        embed = disnake.Embed(
            title=f"Do you want to make {character.name} your main character?",
            color=disnake.Color.purple(),
        )
        embed.set_image(url=f"https://media.singularityapp.online/images/cards/{character.id}.png")
        view = Confirm(Interaction)
        await Interaction.channel.send(embed=embed, view=view)
        await wait_for(view)
        Interaction = view.interaction
        if not view.value:
            embed = disnake.Embed(
                title=f"{character.name} was not set as your main character.",
                color=disnake.Color.purple(),
            )
            embed.set_image(url=f"https://media.singularityapp.online/images/cards/{character.id}.png")
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return
        if len(user.main_characters) < 3:
            embed = disnake.Embed(
                title=f"{character.name} has been set as your main character.",
                color=disnake.Color.purple(),
            )
            if premium:
                user.pcharacter_storage = storage
            else:
                user.character_storage = storage
            user.main_characters.append(character)
            await user.update()
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return
        view = CharacterSelectDropdown(Interaction, user.main_characters)
        embed = disnake.Embed(
            title="Choose a character to replace",
            color=disnake.Color.purple(),
        )
        await Interaction.response.edit_message(embed=embed, view=view)
        await wait_for(view)
        character2 = user.main_characters.pop(view.value)
        storage.append(character2)
        if premium:
            user.pcharacter_storage = storage
        else:
            user.character_storage = storage
        user.main_characters.append(character)
        embed = disnake.Embed(
            title=f"{character.name} has replaced {character2.name} as your main character.",
            color=disnake.Color.purple(),
        )
        await user.update()
        await Interaction.channel.send(embed=embed)

    @character.sub_command(name="store", description="store a main character into storage")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def store(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        
        embed = disnake.Embed(
            title="Choose a main character to store",
            color=disnake.Color.purple(),
        )
        for character in user.main_characters:
            typequal = ""
            for _t,_q in zip(character.etypes,character.equalities):
                typequal+=f"{_t.emoji} {_q.emoji}\n"
            embed.add_field(name=f"{character.name}{converter[character.rarity]}",value=typequal)
        view = CharacterSelectDropdown(Interaction, user.main_characters)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character = user.main_characters.pop(view.value)
        msg = add_to_available_storage(user, character, skip_main=True)
        if msg:
            embed = disnake.Embed(
                title=f"{character.name} was stored in {msg}",
                color=disnake.Color.purple(),
            )
            embed.set_image(url=f"https://media.singularityapp.online/images/cards/{character.id}.png")
            await user.update()
            await Interaction.channel.send(embed=embed)
            return
        embed = disnake.Embed(
            title=f"You storage is full {character.name} is still a main character",
            color=disnake.Color.purple(),
        )
        embed.set_image(url=f"https://media.singularityapp.online/images/cards/{character.id}.png")
        await Interaction.channel.send(embed=embed)

    @character.sub_command(
        name="ascend", description="ascend a main character to a higher plain of existence"
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def awake(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        embed = disnake.Embed(
            title="Select a character to awake", color=disnake.Color.blue()
        )
        view = CharacterSelectDropdown(Interaction, user.main_characters)

        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character: Character = user.main_characters[view.value]
        if character.level >= 100 and character.awaken < 3:
            embed = disnake.Embed(
                title="your character has reached a new peak"
                ,
                color=disnake.Color.purple(),
            )
            character.awaken += 1
            character.xp = 0
            await user.update()
            await Interaction.channel.send(embed=embed)
            return
        embed = disnake.Embed(
            title="Your character has reach it's peak or isn't level 100", color=disnake.Color.purple()
        )
        await Interaction.channel.send(embed=embed)
    
"""    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @stand.sub_command(name="trade", description="trade a stand with someone else")
    async def trade(
        self, Interaction: disnake.ApplicationCommandInteraction, tradee: disnake.Member
    ):
        translation = await self.stfubot.database.get_interaction_lang(Interaction)
        user1 = await self.stfubot.database.get_user_info(Interaction.author.id)
        user1.discord = Interaction.author

        if True:
            embed = disnake.Embed(
                title="An error has occurred",
                description="This command is disabled while we investigate a bug",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://storage.stfurequiem.com/randomAsset/avatar.png"
            )
            await Interaction.send(embed=embed)
            return
        
        if tradee == user1.discord:
            embed = disnake.Embed(
                title="An error has occurred",
                description="You can't trade with yourself...",
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url="https://storage.stfurequiem.com/randomAsset/avatar.png"
            )
            await Interaction.send(embed=embed)
            return
        if not await self.stfubot.database.user_in_database(tradee.id):
            embed = disnake.Embed(
                title="An error has occurred",
                description=f"It seems {tradee.display_name} is not in the database, consider using .ad first !",
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url="https://storage.stfurequiem.com/randomAsset/avatar.png"
            )
            await Interaction.send(embed=embed)
            return
        user2 = await self.stfubot.database.get_user_info(tradee.id)
        user2.discord = tradee
        tradeUrl = "https://cdn0.iconfinder.com/data/icons/trading-outline/32/trading_outline_2._Location-512.png"
        embed = disnake.Embed(
            title=f"Trade between {Interaction.author.display_name} and {tradee.display_name}",
            description=f"{tradee.display_name}, do you want to trade with {Interaction.author.display_name} ?",
        )
        embed.set_thumbnail(url=tradeUrl)
        view = Confirm(Interaction, custom_user=tradee)
        await Interaction.send(embed=embed, view=view)
        time_out = await view.wait()
        if time_out:
            raise asyncio.TimeoutError
        if not view.value:
            embed = disnake.Embed(
                title="Error",
                description=f"{tradee.display_name} refused the trade",
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url="https://storage.stfurequiem.com/randomAsset/avatar.png"
            )
            await Interaction.response.edit_message(embed=embed, view=None)
            return

        if user1.stands == [] or user2.stands == []:
            embed = disnake.Embed(
                title="An error has occurred",
                description=f"It seems one of you don't have any stand",
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url="https://storage.stfurequiem.com/randomAsset/avatar.png"
            )
            await Interaction.response.edit_message(embed=embed, view=None)
            return
        embed = disnake.Embed(
            title=f"{Interaction.author.display_name}, Which stand would you like to trade ?"
        )
        embed.set_thumbnail(url=tradeUrl)
        stands = []
        # get the second stand to exange
        for i, s in enumerate(User1["main_stand"]):
            stands.append([self.fixpool[s[0] - 1], s[1], i])
        for i, s in enumerate(stands):
            stars = "⭐" * s[0]["stars"] + "🌟" * s[1]
            embed.add_field(
                name=f"｢{s[0]['stand_name']}｣:{i+1}",
                value=f"{stars}",
                inline=False,
            )
        view = StandSelectDropdown(Interaction, User1["main_stand"])
        await Interaction.edit_original_message(embed=embed, view=view)
        time_out = await view.wait()
        if time_out:
            raise asyncio.TimeoutError
        choix1 = view.value
        # get the first stand to exange
        stands = []
        embed = disnake.Embed(
            title=f"{user.display_name}, which stand would you like to trade ?"
        )
        embed.set_thumbnail(url=tradeUrl)
        for i, s in enumerate(User2["main_stand"]):
            stands.append([self.fixpool[s[0] - 1], s[1], i])
        for i, s in enumerate(stands):
            stars = "⭐" * s[0]["stars"] + "🌟" * s[1]
            embed.add_field(
                name=f"｢{s[0]['stand_name']}｣:{i+1}",
                value=f"{stars}",
                inline=False,
            )
        view = StandSelectDropdown(Interaction, User2["main_stand"], custom_user=user)
        await Interaction.edit_original_message(embed=embed, view=view)
        time_out = await view.wait()
        if time_out:
            raise asyncio.TimeoutError
        choix2 = int(view.children[0].values[0])
        users = [user, Interaction.author]

        stands = []
        stands.append(
            [
                self.fixpool[User1["main_stand"][choix1][0] - 1],
                User1["main_stand"][choix1][1],
                0,
            ]
        )
        stands.append(
            [
                self.fixpool[User2["main_stand"][choix2][0] - 1],
                User2["main_stand"][choix2][1],
                1,
            ]
        )
        for user_ in users:
            embed = disnake.Embed(
                title=f"{user_.display_name}, do you accept the trade ?"
            )
            embed.set_thumbnail(url=tradeUrl)
            for i, s in enumerate(stands):
                stars = "⭐" * s[0]["stars"] + "🌟" * s[1]
                if s[1] > 1:
                    stars = "🌟" * s[0]["stars"] + "🌠" * s[1]
                embed.add_field(
                    name=f"{users[not(i)].display_name} get:",
                    value=f"｢{s[0]['stand_name']}｣ {stars}",
                    inline=False,
                )
            view = Confirm(Interaction, custom_user=user_)
            await Interaction.edit_original_message(embed=embed, view=view)
            if await view.wait():
                raise asyncio.TimeoutError
            if not view.value:
                embed = disnake.Embed(
                    title="Error",
                    description=f"{user_.display_name} refused the trade",
                    color=0xFF0000,
                )
                embed.set_thumbnail(
                    url="https://storage.stfurequiem.com/randomAsset/avatar.png"
                )
                await Interaction.edit_original_message(embed=embed, view=None)
                return
        User1["main_stand"][choix1], User2["main_stand"][choix2] = (
            User2["main_stand"][choix2],
            User1["main_stand"][choix1],
        )
        await self.database.Update(User1)
        await self.database.Update(User2)
        embed = disnake.Embed(title=f"Done, the trade was successful !")
        await Interaction.edit_original_message(embed=embed, view=None)
"""
def setup(client: SingularityBot):
    client.add_cog(management(client))