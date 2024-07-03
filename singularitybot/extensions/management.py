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
from singularitybot.models.gameobjects.character import Character, Types, Qualities

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
        self.active_trades = set()  # To keep track of active trades

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
            await Interaction.send(embed=embed)
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
                await Interaction.send(embed=embed)
                return
            await Interaction.channel.send(embed=embed)
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
            color=disnake.Color.dark_purple(),
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
        await Interaction.response.edit_message(embed=embed, view=PlaceHolder())

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
                await Interaction.send(embed=embed)
                return
            await Interaction.channel.send(embed=embed)
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
            title="Select a character to awake", color=disnake.Color.dark_purple()
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
    @character.sub_command(name="reforge", description="Reforge a main character for 10000 fragments")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def reforge(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        if user.fragments < 10000:
            embed = disnake.Embed(
                title="Insufficient Fragments",
                description=f"You need 10000 fragments to reforge a character. You currently have {user.fragments} fragments.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return

        if not user.main_characters:
            embed = disnake.Embed(
                title="No Main Characters",
                description="You don't have any main characters to reforge.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title="Select a character to reforge",
            color=disnake.Color.dark_purple(),
        )
        view = CharacterSelectDropdown(Interaction, user.main_characters)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character = user.main_characters[view.value]
        index = view.value
        embed = disnake.Embed(
            title=f"Are you sure you want to reforge {character.name} for 10000 {CustomEmoji.FRAGMENTS}?",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url="https://media1.tenor.com/m/W3PYGHqtkUMAAAAd/forge-dwarf.gif")
        view = Confirm(Interaction)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        Interaction = view.interaction

        if not view.value:
            embed = disnake.Embed(
                title="Reforge Cancelled",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url="https://media1.tenor.com/m/W3PYGHqtkUMAAAAd/forge-dwarf.gif")
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return

        # Deduct the cost and reforge the character
        user.fragments -= 10000
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
        

        character.types = [t.name for t in pulled_types]
        character.qualities = [q.name for q in pulled_qualities]
        character = Character(character.to_dict())
        user.main_characters[index] = character
        await user.update()

        embed = disnake.Embed(
            title=f"{character.name} has been reforged!",
            color=disnake.Color.dark_purple(),
        )
        embed = character_field(character,embed)
        await Interaction.response.edit_message(embed=embed, view=PlaceHolder())

    @character.sub_command(name="trade", description="trade a character with another user")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def trade(
        self, Interaction: disnake.ApplicationCommandInteraction, tradee: disnake.User
    ):
        user1 = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user1.discord = Interaction.author

        if tradee.id == user1.discord.id:
            embed = disnake.Embed(
                title="Error",
                description="You can't trade with yourself.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return

        if not await self.singularitybot.database.user_in_database(tradee.id):
            embed = disnake.Embed(
                title="Error",
                description=f"{tradee.display_name} is not in the database. They need to use the bot first!",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return

        user2 = await self.singularitybot.database.get_user_info(tradee.id)
        user2.discord = tradee

        if (user1.id, user2.id) in self.active_trades or (user2.id, user1.id) in self.active_trades:
            embed = disnake.Embed(
                title="Error",
                description="A trade between you two is already in progress.",
                color=disnake.Color.red(),
            )
            await Interaction.send(embed=embed)
            return

        self.active_trades.add((user1.id, user2.id))
        trade_url = "https://cdn0.iconfinder.com/data/icons/trading-outline/32/trading_outline_2._Location-512.png"
        
        try:
            embed = disnake.Embed(
                title=f"Trade Request",
                description=f"{tradee.display_name}, do you want to trade with {Interaction.author.display_name}?",
                color=disnake.Color.dark_purple(),
            )
            embed.set_thumbnail(url=trade_url)
            view = Confirm(Interaction, user=tradee)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)

            if not view.value:
                embed = disnake.Embed(
                    title="Trade Refused",
                    description=f"{tradee.display_name} refused the trade.",
                    color=disnake.Color.red(),
                )
                await Interaction.edit_original_message(embed=embed, view=None)
                return

            if not user1.main_characters or not user2.main_characters:
                embed = disnake.Embed(
                    title="Error",
                    description="One of you doesn't have any main characters to trade.",
                    color=disnake.Color.red(),
                )
                await Interaction.edit_original_message(embed=embed, view=None)
                return

            # Select character from user1
            embed = disnake.Embed(
                title=f"{Interaction.author.display_name}, select a character to trade:",
                color=disnake.Color.dark_purple(),
            )
            view = CharacterSelectDropdown(Interaction, user1.main_characters)
            await Interaction.edit_original_message(embed=embed, view=view)
            await wait_for(view)
            choice1 = view.value

            # Select character from user2
            embed = disnake.Embed(
                title=f"{tradee.display_name}, select a character to trade:",
                color=disnake.Color.dark_purple(),
            )
            view = CharacterSelectDropdown(Interaction, user2.main_characters, custom_user=tradee)
            await Interaction.edit_original_message(embed=embed, view=view)
            await wait_for(view)
            choice2 = view.value

            char1 = user1.main_characters.pop(choice1)
            char2 = user2.main_characters.pop(choice2)
            # Perform the trade by updating the users
            await user1.update()
            await user2.update()

            # Confirm the trade
            embed = disnake.Embed(
                title="Confirm Trade",
                description=f"{Interaction.author.display_name} will trade {char1.name} with {tradee.display_name}'s {char2.name}. Do you both accept?",
                color=disnake.Color.dark_purple(),
            )
            embed.set_thumbnail(url=trade_url)
            view = Confirm(Interaction)
            await Interaction.edit_original_message(embed=embed, view=view)
            await wait_for(view)

            if not view.value:
                
                embed = disnake.Embed(
                    title="Trade Cancelled",
                    description="The trade was cancelled.",
                    color=disnake.Color.red(),
                )
                # Perform the trade by updating the users
                user1.main_characters.insert(choice1, char1)
                user2.main_characters.insert(choice2, char2)
                await user1.update()
                await user2.update()
                await Interaction.edit_original_message(embed=embed, view=None)
                return

            

            user1.main_characters.append(char2)
            user2.main_characters.append(char1)

            await user1.update()
            await user2.update()

            embed = disnake.Embed(
                title="Trade Successful",
                description=f"{Interaction.author.display_name} traded {char1.name} with {tradee.display_name}'s {char2.name}.",
                color=disnake.Color.green(),
            )
            await Interaction.edit_original_message(embed=embed, view=None)
        except Exception as e:
            embed = disnake.Embed(
                title="Error",
                description="An error occurred during the trade. Please try again.",
                color=disnake.Color.red(),
            )
            await Interaction.edit_original_message(embed=embed, view=None)
            print(f"Error during trade: {e}")
        finally:
            self.active_trades.discard((user1.id, user2.id))
def setup(client: SingularityBot):
    client.add_cog(management(client))