import disnake
import datetime
import pickle
import json

from disnake.ext import tasks,commands

from singularitybot.globals.variables import GANGCREATIONCOST, GANGURL,PLAYER_XPGAINS,CHARACTER_XPGAINS,FRAGMENTSGAIN
# ui
from singularitybot.ui.storage.ChooseDonor import ChooseStorage
from singularitybot.ui.CharacterSelect import CharacterSelectDropdown
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.place_holder import PlaceHolder
from singularitybot.ui.paginator import Menu
from singularitybot.ui.galaxy.galaxy_creation_prompt import GalaxyModal
from singularitybot.ui.galaxy.galaxy_join_select import GalaxySelectDropdown

# utils
from singularitybot.utils.decorators import database_check, galaxy_check, galaxy_rank_check
from singularitybot.utils.functions import format_combat_log,wait_for, add_to_available_storage, is_url_image, create_fight_handler_request, wait_for_fight_end, storage_from_autocomplete

# singularitybot model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.globals.emojis import CustomEmoji,converter
from singularitybot.models.gameobjects.galaxy import Galaxy, GalaxyRank

with open("singularitybot/data/raids/current_raid.json") as file:
    current_raid = json.load(file)

class Galaxies(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot
    # GALAXY MAIN COMMANDS
    @commands.slash_command(name="galaxy", description="Galaxies related commands")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @database_check()
    async def galaxy(self, Interaction: disnake.CommandInteraction):
        pass

    @galaxy.sub_command(name="create", description="Create a new galaxy")
    async def create(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        entry = f"{GANGCREATIONCOST}{CustomEmoji.FRAGMENTS}"
        balance = f"{user.fragments}{CustomEmoji.FRAGMENTS}"

        if not user.galaxy_id is None:
            embed = disnake.Embed(
                title="You already have a galaxy, leave your galaxy to create a new one!",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=GANGURL)
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title=f"You need to pay {entry} to create a new galaxy, you have: {balance}",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=GANGURL)
        view = Confirm(Interaction)

        await Interaction.send(embed=embed, view=view)
        await wait_for(view)

        Interaction = view.interaction  # type: ignore

        if not view.value:
            embed = disnake.Embed(
                title="You can create a galaxy anytime!", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=GANGURL)
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return

        if user.fragments < GANGCREATIONCOST:
            amount = f"{GANGCREATIONCOST - user.fragments}{CustomEmoji.FRAGMENTS}"
            embed = disnake.Embed(
                title=f"You don't have enough money, you need {amount} to create a galaxy",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=GANGURL)
            await Interaction.response.edit_message(embed=embed, view=PlaceHolder())
            return

        user.fragments -= GANGCREATIONCOST
        modal = GalaxyModal()
        await Interaction.response.send_modal(modal=modal)  # type: ignore
        modal_inter: disnake.ModalInteraction = await self.singularitybot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_galaxy"
            and i.author.id == Interaction.author.id,
            timeout=300,
        )

        galaxy_name = modal_inter.text_values["galaxy_name"]
        galaxy_motd = modal_inter.text_values["galaxy_motd"]
        galaxy_motto = modal_inter.text_values["galaxy_motto"]

        user.galaxy_id = await self.singularitybot.database.add_galaxy(
            user.id, galaxy_name, galaxy_motd, galaxy_motto
        )
        await user.update()

    @galaxy.sub_command(name="join", description="Join a new galaxy")
    async def join(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        if not user.galaxy_id is None:
            embed = disnake.Embed(
                title="You already have a galaxy, leave your galaxy to join a new one",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=GANGURL)
            await Interaction.send(embed=embed)
            return

        galaxies = [
            await self.singularitybot.database.get_galaxy_info(i) for i in user.galaxies_invites
        ]

        if len(galaxies) == 0:
            embed = disnake.Embed(
                title="You have no galaxy invites, ask the leader or a member to invite you",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=GANGURL)
            await Interaction.send(embed=embed)
            return
        embed = disnake.Embed(
            title="Select a galaxy",
            color=disnake.Color.dark_purple(),
        )
        view = GalaxySelectDropdown(Interaction, galaxies)
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)

        galaxy = galaxies[view.value]

        embed = disnake.Embed(
            title=f"You joined {galaxy.name}",
            color=disnake.Color.dark_purple(),
        )
        galaxy.users.append(user.id)
        galaxy.ranks[user.id] = GalaxyRank.STARDUST.value
        user.galaxy_id = galaxy.id
        user.galaxies_invites = []

        await galaxy.update()
        await user.update()

        await Interaction.send(embed=embed)

    @galaxy_check()
    @galaxy.sub_command(name="leave", description="Leave your current galaxy")
    async def leave(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if galaxy.ranks[user.id] == GalaxyRank.BOSS:
            if len(galaxy.users) == 1:
                # Only member, can leave and disband the galaxy
                galaxy.users.remove(user.id)
                user.galaxy_id = None
                await user.update()
                await self.singularitybot.database.delete_galaxy(user.galaxy_id)
                embed = disnake.Embed(
                    title="You have left and disbanded the galaxy.",
                    color=disnake.Color.dark_purple(),
                )
            else:
                embed = disnake.Embed(
                    title="You are the leader of the galaxy. You must promote someone else to leader before leaving.",
                    color=disnake.Color.dark_purple(),
                )
            await Interaction.send(embed=embed)
            return

        # Non-leader member can leave freely
        galaxy.users.remove(user.id)
        del galaxy.ranks[user.id]
        user.galaxy_id = None
        await user.update()
        await galaxy.update()

        embed = disnake.Embed(
            title="You have left the galaxy.",
            color=disnake.Color.dark_purple(),
        )
        await Interaction.send(embed=embed)
             
    @galaxy_check()
    @galaxy.sub_command(name="show", description="Show your galaxy info")
    async def show(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        member_names = []
        for member_id in galaxy.users:
            member = await self.singularitybot.get_or_fetch_user(int(member_id))
            member_names.append(member.name if member else "Unknown User")

        ranks = [GalaxyRank.BOSS, GalaxyRank.STAR, GalaxyRank.STARDUST]

        embed = disnake.Embed(
            title=galaxy.name, description=galaxy.motto, color=disnake.Color.dark_purple()
        )
        embed.set_image(url=galaxy.image_url)
        embed.add_field(
            name="`MOTD`",
            value=galaxy.motd,
            inline=False,
        )
        embed.add_field(
            name=f"`Members: {len(galaxy.users)}`",
            value=f"\n           ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            inline=False,
        )
        for i, u in enumerate(galaxy.users):
            embed.add_field(
                name=f"`{member_names[i]}`",
                value=f"rank:{ranks[galaxy.ranks[u]].name}",
                inline=True,
            )

        if len(galaxy.characters) == 0:
            embed.add_field(
                name="`Guarding Characters`",
                value=f"`None`\n           ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
                inline=False,
            )
        else:
            embed.add_field(
                name="`Guarding Characters`",
                value=f"\n           ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
                inline=False,
            )
            for character in galaxy.characters:
                typequal = ""
                for _t,_q in zip(character.etypes,character.equalities):
                    typequal+=f"{_t.emoji} {_q.emoji}\n"
                embed.add_field(name=f"{character.name}{converter[character.rarity]}",value=typequal,inline=True)
        embed.add_field(
            name="`Statistics`",
            value=f"\n           ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            inline=False,
        )
        embed.add_field(
            name="vault",
            value=f"`{galaxy.vault}`|{CustomEmoji.FRAGMENTS}\n",
        )
        embed.add_field(
            name="elo",
            value=f"`{galaxy.war_elo}`|🏆\n",
        )

        await Interaction.send(embed=embed)

    # CHARACTER GUARD MANAGEMENT
    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @galaxy.sub_command_group(name="character")
    async def character(self, Interaction: disnake.CommandInteraction):
        pass

    @galaxy_check()
    @character.sub_command(name="add", description="Add a character to guard your galaxy")
    async def add(self, Interaction: disnake.CommandInteraction,storage:str):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        storage,id = storage_from_autocomplete(storage,user)
        
        if galaxy.characters == 3:
            embed = disnake.Embed(
                title="You cannot add anymore characters to defend your galaxy",
                color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        if not storage:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        if len(storage) == 0:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            
            await Interaction.send(embed=embed)
                

        view = CharacterSelectDropdown(Interaction, storage)
        embed = disnake.Embed(
            title="Select a character to protect your galaxy", color=disnake.Color.dark_purple()
        )
        if Interaction.response.is_done():
            await Interaction.send(embed=embed,view=view)
        await Interaction.channel.send(embed=embed,view=view)
        await wait_for(view)
        character = storage.pop(view.value)  # type: ignore
        galaxy.characters.append(character)
        user.update_storage(storage,id)
        embed = disnake.Embed(
            title=f"{character.name} will now be defending your galaxy",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await user.update()
        await galaxy.update()
        await Interaction.channel.send(embed=embed)

    @galaxy_check()
    @character.sub_command(
        name="remove", description="Remove a character from guarding your galaxy"
    )
    async def remove(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if len(galaxy.characters) == 0:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            if Interaction.response.is_done():
                await Interaction.send(embed=embed)
                return
            await Interaction.channel.send(embed=embed)
            return

        view = CharacterSelectDropdown(Interaction, galaxy.characters)
        embed = disnake.Embed(
            title="Select a character to remove", color=disnake.Color.dark_purple()
        )
        if Interaction.response.is_done():
            await Interaction.send(embed=embed,view=view)
        await Interaction.channel.send(embed=embed,view=view)
        await wait_for(view)
        character = galaxy.characters.pop(view.value)  # type: ignore
        msg = add_to_available_storage(user, character, skip_main=True)
        if not msg:
            embed = disnake.Embed(
                title="There is no available storage space, use `/character remove` to free up some space, or donate!",
                color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return
        await user.update()
        await galaxy.update()
        embed = disnake.Embed(
            title=f"The character was stored in: {msg}", color=disnake.Color.dark_purple()
        )
        embed.set_image(url=galaxy.image_url)
        if Interaction.response.is_done():
            await Interaction.send(embed=embed)
        await Interaction.channel.send(embed=embed)
    # MEMBER MANAGEMENT
    @galaxy_check()
    @galaxy.sub_command_group(name="manage")
    async def manage(self, Interaction: disnake.CommandInteraction):
        pass

    @galaxy_rank_check(minimum_rank=GalaxyRank.STAR)
    @manage.sub_command(name="invite", description="Invite someone into your galaxy")
    async def invite(self, Interaction: disnake.CommandInteraction, user: disnake.User):
        User = user
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        user2 = await self.singularitybot.database.get_user_info(User.id)
        user2.discord = User

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)
        if user2.galaxy_id != None:
            embed = disnake.Embed(
                title="This user is already in a galaxy", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        if galaxy.id in user2.galaxies_invites:
            embed = disnake.Embed(
                title="This user has already been invited to join the galaxy", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title=f"You invited {user2.discord.name} to {galaxy.name}",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        user2.galaxies_invites.append(galaxy.id)
        await user2.update()
        await Interaction.send(embed=embed)

    @galaxy_rank_check(minimum_rank=GalaxyRank.STAR)
    @manage.sub_command(name="kick", description="Kick someone from your galaxy")
    async def kick(
        self, Interaction: disnake.CommandInteraction, offender: disnake.User
    ):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        user2 = await self.singularitybot.database.get_user_info(offender.id)
        user2.discord = offender

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if not (user2.id in galaxy.users):
            embed = disnake.Embed(
                title="This user is not in your galaxy", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        rank1 = galaxy.ranks[user.id]
        rank2 = galaxy.ranks[user2.id]
        if rank1 >= rank2:
            embed = disnake.Embed(
                title="You have no permission to kick this user", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        user2.galaxy_id = None
        del galaxy.ranks[user2.id]
        galaxy.users.remove(user2.id)

        await galaxy.update()
        await user2.update()
        embed = disnake.Embed(
            title=f"{user2.discord.name} was kicked from {galaxy.name}",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @manage.sub_command(name="promote", description="Promote a user of your galaxy")
    async def promote(
        self, Interaction: disnake.CommandInteraction, member: disnake.User
    ):
        User = member
        user2 = await self.singularitybot.database.get_user_info(User.id)
        user2.discord = User
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if  user2.galaxy_id == None or user2.galaxy_id != galaxy.id or not (user2.id in galaxy.users):
            embed = disnake.Embed(
                title="This user is not in your galaxy", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        rank = galaxy.ranks[user2.id]
        if rank == GalaxyRank.STAR:
            embed = disnake.Embed(
                title=f"You are about to make {user2.discord.name} the galaxy boss, are you sure?",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            view = Confirm(Interaction)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)
            Interaction = view.interaction  # type: ignore

            if not view.value:
                embed = disnake.Embed(
                    title=f"{user2.discord.name} was not made the galaxy leader",
                    color=disnake.Color.dark_purple(),
                )
                embed.set_image(url=galaxy.image_url)
                await Interaction.send(embed=embed)
                return
            galaxy.ranks[user2.id], galaxy.ranks[user.id] = (
                galaxy.ranks[user.id],
                galaxy.ranks[user2.id],
            )
            embed = disnake.Embed(
                title=f"{user2.discord.name} was made the new galaxy leader",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        galaxy.ranks[user2.id] = GalaxyRank.STAR.value
        await galaxy.update()
        embed = disnake.Embed(
            title=f"You have promoted {user2.discord.name} to {GalaxyRank.STAR.name}",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @manage.sub_command(name="demote", description="Demote a user of your galaxy")
    async def demote(
        self, Interaction: disnake.CommandInteraction, member: disnake.User
    ):
        User = member

        user2 = await self.singularitybot.database.get_user_info(User.id)
        user2.discord = User
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if not (user2.id in galaxy.users) or user2.galaxy_id != None:
            embed = disnake.Embed(
                title="This user is not in your galaxy", color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        rank = galaxy.ranks[user2.id]

        if rank == GalaxyRank.STARDUST:
            pass

        galaxy.ranks[user2.id] = GalaxyRank.STARDUST.value
        await galaxy.update()
        embed = disnake.Embed(
            title=f"You have demoted {user2.discord.name} to {GalaxyRank.STARDUST.value}",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @manage.sub_command(name="changeimage", description="Change your galaxy image")
    async def changeimage(self, Interaction: disnake.CommandInteraction, url: str):
        if is_url_image(url) == False:
            embed = disnake.Embed(
                title="URL Error",
                description="Please add a valid URL",
                color=disnake.Colour.red(),
            )
            await Interaction.send(embed=embed)
            return
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)
        galaxy.image_url = url
        await galaxy.update()
        embed = disnake.Embed(
            title="Your galaxy's image was changed", color=disnake.Color.dark_purple()
        )
        embed.set_image(url=url)
        await Interaction.send(embed=embed)

    # VAULT MANAGEMENT
    @galaxy_check()
    @galaxy.sub_command_group(name="vault")
    async def vault(self, Interaction: disnake.CommandInteraction):
        pass

    @galaxy_check()
    @vault.sub_command(name="deposit", description="Deposit money into your galaxy vault")
    async def deposit(self, Interaction: disnake.CommandInteraction, ammount: int):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if ammount > user.fragments:
            embed = disnake.Embed(
                title="You don't have enough money",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        galaxy.vault += ammount
        user.fragments -= ammount

        ammount_str = f"{ammount}{CustomEmoji.FRAGMENTS}"

        await galaxy.update()
        await user.update()

        embed = disnake.Embed(
            title=f"{ammount_str} was added to the galaxy vault",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @vault.sub_command(name="pay", description="Pay someone in your galaxy")
    async def pay(
        self,
        Interaction: disnake.CommandInteraction,
        member: disnake.User,
        ammount: int,
    ):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        user2 = await self.singularitybot.database.get_user_info(member.id)
        user2.discord = member

        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if ammount > galaxy.vault:
            embed = disnake.Embed(
                title="You don't have enough money",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        galaxy.vault -= ammount
        user2.fragments += ammount

        ammount_str = f"{ammount}{CustomEmoji.FRAGMENTS}"

        await galaxy.update()
        await user2.update()

        embed = disnake.Embed(
            title=f"{ammount_str} was removed from the vault, {user2.discord.name} was paid!",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    # WAR COMMANDS
    @galaxy_check()
    @galaxy.sub_command_group(name="war")
    async def war(self, Interaction: disnake.CommandInteraction):
        pass
    @galaxy_rank_check(minimum_rank=GalaxyRank.STAR)                
    @war.sub_command(name="start",description="Start a war with a random galaxy")   
    async def warstart(self,Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if not galaxy.characters:
            embed = disnake.Embed(
                title="Your galaxy need to have a character to engage in a war",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return
        
        if await self.singularitybot.database.check_active_war(galaxy.id):
            embed = disnake.Embed(
                title="Your galaxy is already in a war or has recently finished one. Please wait.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        await self.singularitybot.database.publish("war_matchmaking_requests", galaxy.id)
        embed = disnake.Embed(
            title="Your galaxy has been added to the matchmaking queue!",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    @war.sub_command(name="status",description="Check if your galaxy is in a war and the current status of the war")
    async def warstatus(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        # Check if the galaxy is currently in a war
        if not await self.singularitybot.database.check_active_war(galaxy.id):
            embed = disnake.Embed(
                title="Your galaxy is not currently in a war.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        # Get the opposing galaxy ID
        opp_id = await self.singularitybot.database.get_active_war(galaxy.id)
        opp_galaxy = await self.singularitybot.database.get_galaxy_info(opp_id)

        # Check if the user has already attacked
        has_attacked = user.id in galaxy.war_attacks

        # Calculate remaining time until the end of the war
        remaining_time = galaxy.end_of_war - datetime.datetime.now()
        remaining_time_str = str(remaining_time).split('.')[0]  # Format remaining time

        embed = disnake.Embed(
            title="War Status",
            color=disnake.Color.dark_purple(),
        )
        embed.add_field(name="Your Galaxy's Damage", value=galaxy.damage_to_current_war, inline=True)
        embed.add_field(name="Opposing Galaxy's Damage", value=opp_galaxy.damage_to_current_war, inline=True)
        embed.add_field(name="Has Attacked", value="Yes" if has_attacked else "No", inline=True)
        embed.add_field(name="Time Until War Ends", value=remaining_time_str, inline=True)
        embed.set_image(url=galaxy.image_url)

        await Interaction.send(embed=embed)
 
    @war.sub_command(name="result",description="See the last war results")
    async def warresult(self,Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        # Get the last war record involving the user's galaxy
        last_war_record = None
        async with await self.singularitybot.database.get_redis_connection() as conn:
            war_records = await conn.hgetall("war_records")
            for war_id, record in war_records.items():
                record_data = pickle.loads(record)
                if galaxy.id in [record_data["winner"], record_data["loser"]]:
                    if not last_war_record or record_data["timestamp"] > last_war_record["timestamp"]:
                        last_war_record = record_data                 
        if not last_war_record:
            embed = disnake.Embed(
                title="No recent war records found for your galaxy.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        winner_galaxy = await self.singularitybot.database.get_galaxy_info(last_war_record["winner"])
        loser_galaxy = await self.singularitybot.database.get_galaxy_info(last_war_record["loser"])

        embed = disnake.Embed(
            title="Last War Result",
            color=disnake.Color.dark_purple(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Winner", value=winner_galaxy.name, inline=True)
        embed.add_field(name="Loser", value=loser_galaxy.name, inline=True)
        embed.add_field(name="Winner Damage", value=last_war_record["winner_damage"], inline=True)
        embed.add_field(name="Loser Damage", value=last_war_record["loser_damage"], inline=True)
        embed.set_image(url=galaxy.image_url)

        await Interaction.send(embed=embed)

    @war.sub_command(name="attack",description="Make an attack on the ennemy galaxy")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def warattack(self,Interaction: disnake.CommandInteraction):

        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)
        
        if not await self.singularitybot.database.check_active_war(galaxy.id):
            embed = disnake.Embed(
                title="Your galaxy is not in a war or has recently finished one. Please ask for your boss to start one.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return
        
        if not user.main_characters:
            embed = disnake.Embed(title="You need to have main characters to fight use `/character main`",colour=disnake.Colour.dark_purple())
            embed.set_image(url="https://media.singularityapp.online/images/assets/notregistered.jpg")
            await Interaction.send(embed=embed)
            return
        
        # check that the person has not done an attack
        
        if user.id in galaxy.war_attacks:
            embed = disnake.Embed(
                title="You already did your attack for this war !",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return
        # get the opposing galaxy ID
        opp_id = await self.singularitybot.database.get_active_war(galaxy.id)
        opp_galaxy = await self.singularitybot.database.get_galaxy_info(opp_id)
        # create the match request
        
        ennemy_data = {
            "name": opp_galaxy.name,
            "avatar": None,
            "main_characters": [
                char.to_dict() for char in opp_galaxy.characters
            ],
        }
        players = [user.id, "0101"]
        channels = [Interaction.channel.id]*2
        shards = [self.singularitybot.shard_id]*2
        names = [user.discord.display_name,ennemy_data["name"]]
        match_request = create_fight_handler_request(players,channels,shards,names,galaxy_fight=True)
        match_request["IA_DATA"] = ennemy_data
        winner,combat_log = await wait_for_fight_end(self.singularitybot.database,match_request)
        damage = combat_log.pop(-1)

        galaxy.damage_to_current_war += damage
        galaxy.war_attacks.append(user.id)
        await galaxy.update()

        embeds = format_combat_log(combat_log)

        final_view = Menu(embeds)
        await Interaction.channel.send(embed=embeds[0], view=final_view)
        embed = disnake.Embed(
            title=f"You cleared {damage}% of the galaxy guardian  and did {damage} damage",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.channel.send(embed=embed)

        user.xp += PLAYER_XPGAINS * (1 + (winner.id == user.id))
        user.fragments += FRAGMENTSGAIN * (1 + (winner.id == user.id))
        for char in user.main_characters:
            char.xp += CHARACTER_XPGAINS * (1 + (winner.id == user.id))
        
        await user.update()

    # RAID COMMANDS
    @galaxy_check()
    @galaxy.sub_command_group(name="raid")
    async def raid(self, Interaction: disnake.CommandInteraction):
        pass
    
    @galaxy_rank_check(minimum_rank=GalaxyRank.STAR)
    @raid.sub_command(name="start", description="Start a raid and try to win items and characters")
    async def raidstart(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if galaxy.damage_to_current_raid > 0 and galaxy.end_of_raid > datetime.datetime.now():
            embed = disnake.Embed(
                title="Your galaxy is already in a raid or has recently finished one. Please wait.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        raid_cost = current_raid["cost"]

        if galaxy.vault < raid_cost:
            embed = disnake.Embed(
                title="Insufficient Funds",
                description=f"Your galaxy does not have enough funds to start this raid. You need {raid_cost} fragments.",
                color=disnake.Color.red(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        # Deduct the cost from the galaxy's vault
        galaxy.vault -= raid_cost

        galaxy.end_of_raid = datetime.datetime.now() + datetime.timedelta(days=1)
        galaxy.damage_to_current_raid = 0
        galaxy.raid_attacks = []

        await galaxy.update()

        embed = disnake.Embed(
            title=f"Your galaxy has started a raid against {current_raid['name']}!",
            description=f"The raid cost {raid_cost} fragments, which has been deducted from your galaxy's vault.",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.send(embed=embed)

    @raid.sub_command(name="status", description="Check if you are in a raid and the current status of the raid")
    async def raidstatus(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if galaxy.end_of_raid <= datetime.datetime.now():
            embed = disnake.Embed(
                title="Your galaxy is not currently in a raid.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        remaining_time = galaxy.end_of_raid - datetime.datetime.now()
        remaining_time_str = str(remaining_time).split('.')[0]  # Format remaining time


        target_damage = current_raid["target_damage"]
        remaining_damage = max(0, target_damage - galaxy.damage_to_current_raid)
        raid_image_url = current_raid["raid_image"]

        embed = disnake.Embed(
            title="Raid Status",
            color=disnake.Color.dark_purple(),
        )
        embed.add_field(name="Your Galaxy's Damage", value=galaxy.damage_to_current_raid, inline=True)
        embed.add_field(name="Remaining Damage for Rewards", value=remaining_damage, inline=True)
        embed.add_field(name="Time Until Raid Ends", value=remaining_time_str, inline=True)
        embed.set_image(url=raid_image_url)

        await Interaction.send(embed=embed)

    @raid.sub_command(name="result", description="See the result of the last raid")
    async def raidresult(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if galaxy.damage_to_current_raid == 0:
            embed = disnake.Embed(
                title="Your galaxy has not participated in a raid recently.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        # Retrieve the last raid record
        raid_id = f"raid_{galaxy.id}"
        raid_record = await self.singularitybot.database.get_raid_record(raid_id)

        if not raid_record:
            embed = disnake.Embed(
                title="No Raid Record Found",
                description="No recent raid records found for your galaxy.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        raid_successful = raid_record["successful"]

        if raid_successful:
            embed = disnake.Embed(
                title="Raid Result",
                description=f"Congratulations! Your galaxy successfully completed the raid and earned rewards!",
                color=disnake.Color.dark_purple(),
            )
            rewards = raid_record["rewards"]
            rewards_str = "\n".join([f"- {reward}" for reward in rewards])
            embed.add_field(name="Rewards", value=rewards_str, inline=False)
        else:
            embed = disnake.Embed(
                title="Raid Result",
                description="Your galaxy failed to complete the raid.",
                color=disnake.Color.dark_purple(),
            )

        # Use the raid image
        raid_image_url = raid_record.get("raid_image", galaxy.image_url)
        embed.set_image(url=raid_image_url)

        await Interaction.send(embed=embed)


    @raid.sub_command(name="attack", description="Attack the current raid")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def raidattack(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if galaxy.end_of_raid < datetime.datetime.now():
            embed = disnake.Embed(
                title="Your galaxy is not currently in a raid or the raid has ended.",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        if not user.main_characters:
            embed = disnake.Embed(title="You need to have main characters to fight use `/character main`", colour=disnake.Colour.dark_purple())
            embed.set_image(url="https://media.singularityapp.online/images/assets/notregistered.jpg")
            await Interaction.send(embed=embed)
            return

        if user.id in galaxy.raid_attacks:
            embed = disnake.Embed(
                title="You already did your attack for this raid!",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        embed = disnake.Embed(color=disnake.Color.dark_purple())
        embed.set_image(url=current_raid["raid_image"])
        await Interaction.send(embed=embed)

        ennemy_data = {
            "name": current_raid["name"],
            "avatar": None,
            "main_characters": current_raid["main_characters"],
        }
        players = [user.id, "0101"]
        channels = [Interaction.channel.id]*2
        shards = [self.singularitybot.shard_id]*2
        names = [user.discord.display_name, ennemy_data["name"]]
        match_request = create_fight_handler_request(players, channels, shards, names, galaxy_raid=True)
        match_request["IA_DATA"] = ennemy_data
        winner, combat_log = await wait_for_fight_end(self.singularitybot.database, match_request)
        damage = combat_log.pop(-1)

        galaxy.damage_to_current_raid += damage
        galaxy.raid_attacks.append(user.id)
        await galaxy.update()

        embeds = format_combat_log(combat_log)

        final_view = Menu(embeds)
        await Interaction.channel.send(embed=embeds[0], view=final_view)
        embed = disnake.Embed(
            title=f"You did {int(damage)} damage to {current_raid['name']}!",
            color=disnake.Color.dark_purple(),
        )
        embed.set_image(url=galaxy.image_url)
        await Interaction.channel.send(embed=embed)

        user.xp += PLAYER_XPGAINS  * (1 + (winner.id == user.id))
        user.fragments += FRAGMENTSGAIN * (1 + (winner.id == user.id))
        for char in user.main_characters:
            char.xp += CHARACTER_XPGAINS * (1 + (winner.id == user.id))

        await user.update()

def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Galaxies(singularitybot))
