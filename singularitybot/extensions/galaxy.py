import disnake
import datetime

from disnake.ext import tasks,commands

from singularitybot.globals.variables import GANGCREATIONCOST, GANGURL

# ui
from singularitybot.ui.storage.ChooseDonor import ChooseStorage
from singularitybot.ui.CharacterSelect import CharacterSelectDropdown
from singularitybot.ui.confirmation import Confirm
from singularitybot.ui.place_holder import PlaceHolder
from singularitybot.ui.galaxy.galaxy_creation_prompt import GalaxyModal
from singularitybot.ui.galaxy.galaxy_join_select import GalaxySelectDropdown

# utils
from singularitybot.utils.decorators import database_check, galaxy_check, galaxy_rank_check
from singularitybot.utils.functions import wait_for, add_to_available_storage, is_url_image

# singularitybot model
from singularitybot.models.bot.singularitybot import SingularityBot
from singularitybot.globals.emojis import CustomEmoji
from singularitybot.models.gameobjects.galaxy import Galaxy, GalaxyRank

class Galaxies(commands.Cog):
    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot
        self.check_active_wars.start()

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
                stars = "⭐" * character.stars + "🌟" * character.ascension
                embed.add_field(
                    name=f"`｢{character.name}｣`|`{stars}`",
                    value=f"`Level: {character.level}`",
                    inline=True,
                )
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
    async def add(self, Interaction: disnake.CommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if galaxy.characters == 3:
            embed = disnake.Embed(
                title="You cannot add anymore characters to defend your galaxy",
                color=disnake.Color.dark_purple()
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        if len(user.character_storage) == 0 and len(user.pcharacter_storage) == 0:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        storage = user.character_storage
        premium = False
        if user.is_donator():
            embed = disnake.Embed(
                title="Choose your storage", color=disnake.Color.dark_purple()
            )
            view = ChooseStorage(Interaction)
            await Interaction.send(embed=embed, view=view)
            await wait_for(view)
            Interaction = view.interaction  # type: ignore
            if not view.value:
                premium = True
                storage = user.pcharacter_storage

        if len(storage) == 0:
            embed = disnake.Embed(
                title="Your storage is empty",
                color=disnake.Color.dark_purple(),
            )
            embed.set_image(url=galaxy.image_url)
            await Interaction.send(embed=embed)
            return

        view = CharacterSelectDropdown(Interaction, storage)
        embed = disnake.Embed(
            title="Select a character to protect your galaxy", color=disnake.Color.dark_purple()
        )
        await Interaction.send(embed=embed, view=view)
        await wait_for(view)
        character = storage.pop(view.value)  # type: ignore
        galaxy.characters.append(character)

        if premium:
            user.pcharacter_storage = storage
        else:
            user.character_storage = storage

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
            await Interaction.send(embed=embed)
            return

        view = CharacterSelectDropdown(Interaction, galaxy.characters)
        embed = disnake.Embed(
            title="Select a character to remove", color=disnake.Color.dark_purple()
        )
        await Interaction.send(embed=embed, view=view)
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
        await Interaction.send(embed=embed)

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
    @tasks.loop(hours=1)
    async def check_active_wars(self):
        now = datetime.datetime.utcnow()
        wars = await self.singularitybot.database.get_active_wars()
        for war in wars:
            if now >= war.end_time:
                await self.end_war(war)

    async def end_war(self, war):
        galaxy1 = await self.singularitybot.database.get_galaxy_info(war.galaxy1_id)
        galaxy2 = await self.singularitybot.database.get_galaxy_info(war.galaxy2_id)
        if war.galaxy1_wins > war.galaxy2_wins:
            winner = galaxy1
            loser = galaxy2
            war.status = "galaxy1"
        elif war.galaxy1_wins < war.galaxy2_wins:
            winner = galaxy2
            loser = galaxy1
            war.status = "galaxy2"
        else:
            war.status = "draw"
            await war.update(self.singularitybot.database)
            return

        # Update Elo and rewards
        winner.war_elo += 50
        loser.war_elo -= 50
        winner.vault += 1000
        loser.vault += 500
        await winner.update()
        await loser.update()
        await war.update(self.singularitybot.database)

    @galaxy.sub_command_group(name="war", description="Galaxy war commands")
    async def war(self, Interaction: disnake.ApplicationCommandInteraction):
        pass
    
    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @war.sub_command(name="start", description="Start a war with another galaxy")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def start_war(self, Interaction: disnake.ApplicationCommandInteraction, target_galaxy_id: int):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if not galaxy:
            await Interaction.send("You are not in a galaxy.", ephemeral=True)
            return

        target_galaxy = await self.singularitybot.database.get_galaxy_info(target_galaxy_id)

        if not target_galaxy:
            await Interaction.send("Target galaxy not found.", ephemeral=True)
            return

        start_time = datetime.datetime.utcnow()
        end_time = start_time + datetime.timedelta(days=3)  # War duration
        war = War(id=None, galaxy1_id=galaxy.id, galaxy2_id=target_galaxy.id, start_time=start_time, end_time=end_time, status="ongoing")

        await self.singularitybot.database.add_war(war)
        await Interaction.send(f"War started with {target_galaxy.name}.", ephemeral=True)

    @war.sub_command(name="status", description="Show the status of ongoing wars")
    async def war_status(self, Interaction: disnake.ApplicationCommandInteraction):
        wars = await self.singularitybot.database.get_active_wars()

        if not wars:
            await Interaction.send("No ongoing wars.", ephemeral=True)
            return

        embed = disnake.Embed(title="Ongoing Wars", color=disnake.Color.red())
        for war in wars:
            galaxy1 = await self.singularitybot.database.get_galaxy_info(war.galaxy1_id)
            galaxy2 = await self.singularitybot.database.get_galaxy_info(war.galaxy2_id)
            embed.add_field(name=f"{galaxy1.name} vs {galaxy2.name}", value=f"Ends at {war.end_time}", inline=False)

        await Interaction.send(embed=embed, ephemeral=True)

    @war.sub_command(name="result", description="Show the result of the last galaxy war")
    async def war_result(self, Interaction: disnake.ApplicationCommandInteraction):
        war = await self.singularitybot.database.get_last_war()

        if not war:
            await Interaction.send("No war history found.", ephemeral=True)
            return

        galaxy1 = await self.singularitybot.database.get_galaxy_info(war.galaxy1_id)
        galaxy2 = await self.singularitybot.database.get_galaxy_info(war.galaxy2_id)
        result = "draw" if war.status == "draw" else (galaxy1.name if war.status == "galaxy1" else galaxy2.name)

        embed = disnake.Embed(title="Last War Result", color=disnake.Color.green())
        embed.add_field(name="Winner", value=result, inline=False)

        await Interaction.send(embed=embed, ephemeral=True)
    # RAID
    @galaxy.sub_command_group(name="raid", description="Galaxy raid commands")
    async def raid(self, Interaction: disnake.ApplicationCommandInteraction):
        pass
    
    @galaxy_rank_check(minimum_rank=GalaxyRank.BOSS)
    @raid.sub_command(name="start", description="Start a raid")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def start_raid(self, Interaction: disnake.ApplicationCommandInteraction, target_id: int):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if not galaxy:
            await Interaction.send("You are not in a galaxy.", ephemeral=True)
            return

        entry_fee = 10000 + 1000 * len(galaxy.members)
        if galaxy.vault < entry_fee:
            await Interaction.send(f"Your galaxy does not have enough fragments. You need {entry_fee} fragments to start a raid.", ephemeral=True)
            return

        start_time = datetime.datetime.utcnow()
        end_time = start_time + datetime.timedelta(hours=1)  # Raid duration
        raid = Raid(id=None, galaxy_id=galaxy.id, target_id=target_id, members=[], start_time=start_time, end_time=end_time, status="ongoing")

        await self.singularitybot.database.add_raid(raid)
        await Interaction.send(f"Raid started against target {target_id}.", ephemeral=True)

    @raid.sub_command(name="status", description="Show the status of ongoing raids")
    async def raid_status(self, Interaction: disnake.ApplicationCommandInteraction):
        raids = await self.singularitybot.database.get_active_raids()

        if not raids:
            await Interaction.send("No ongoing raids.", ephemeral=True)
            return

        embed = disnake.Embed(title="Ongoing Raids", color=disnake.Color.blue())
        for raid in raids:
            galaxy = await self.singularitybot.database.get_galaxy_info(raid.galaxy_id)
            embed.add_field(name=f"Raid by {galaxy.name}", value=f"Ends at {raid.end_time}", inline=False)

        await Interaction.send(embed=embed, ephemeral=True)

    @raid.sub_command(name="participate", description="Participate in an ongoing raid")
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def participate_in_raid(self, Interaction: disnake.ApplicationCommandInteraction):
        user = await self.singularitybot.database.get_user_info(Interaction.author.id)
        user.discord = Interaction.author
        galaxy = await self.singularitybot.database.get_galaxy_info(user.galaxy_id)

        if not galaxy:
            await Interaction.send("You are not in a galaxy.", ephemeral=True)
            return

        raid = await self.singularitybot.database.get_active_raid(galaxy.id)

        if not raid:
            await Interaction.send("No active raid found for your galaxy.", ephemeral=True)
            return

        raid.members.append(user.id)
        await raid.update(self.singularitybot.database)

        await Interaction.send(f"You have joined the raid.", ephemeral=True)

    @raid.sub_command(name="result", description="Show the result of the last raid")
    async def raid_result(self, Interaction: disnake.ApplicationCommandInteraction):
        raid = await self.singularitybot.database.get_last_raid()

        if not raid:
            await Interaction.send("No raid history found.", ephemeral=True)
            return

        galaxy = await self.singularitybot.database.get_galaxy_info(raid.galaxy_id)
        result = "success" if raid.status == "success" else "failure"

        embed = disnake.Embed(title="Last Raid Result", color=disnake.Color.orange())
        embed.add_field(name="Result", value=result, inline=False)

        await Interaction.send(embed=embed, ephemeral=True)



def setup(singularitybot: SingularityBot):
    singularitybot.add_cog(Galaxies(singularitybot))
