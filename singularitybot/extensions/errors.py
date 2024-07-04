import disnake
import asyncio
import traceback
import topgg
from datetime import datetime
from logging import warning

# utils
from singularitybot.utils.functions import view_timeout

# stfu model
from singularitybot.models.bot.singularitybot import SingularityBot


from disnake.ext import commands
from disnake.ext.commands import errors


class ErrorHandle(commands.Cog):
    """ Handle error for the bot """

    def __init__(self, singularitybot: SingularityBot):
        self.singularitybot = singularitybot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        error: commands.errors.CommandError,
    ) -> None:
        await self.handle_error(Interaction, error)

    @commands.Cog.listener()
    async def on_message_command_error(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        error: commands.errors.CommandError,
    ) -> None:
        await self.handle_error(Interaction, error)

    @commands.Cog.listener()
    async def on_user_command_error(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        error: commands.errors.CommandError,
    ) -> None:
        await self.handle_error(Interaction, error)

    @commands.Cog.listener()
    async def on_slash_command_error(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        error: commands.errors.CommandError,
    ) -> None:
        await self.handle_error(Interaction, error)

    async def handle_error(
        self,
        Interaction: disnake.ApplicationCommandInteraction,
        error: errors.CommandError,
    ):
        """
        this listen for error and handle them in this order

        Beforhand save data if any

        1-Know if the error need to be ignored.
        2-Else Notify the user that an error occurred
        3-Log the error
        4-Warn in the console
        """
        # ignore ctx commands
        if isinstance(Interaction, commands.Context):
            return
        # get the command where the error occurred
        command = Interaction.application_command
        # ignore these Exception
        ignore = [
            errors.CommandNotFound,
            errors.CheckFailure,
            # RuntimeError,
        ]
        # if it's an invokeError we get what caused it
        if isinstance(error, commands.errors.CommandInvokeError):
            error = error.original

        # check if the error should be ignored
        if any([isinstance(error, exception) for exception in ignore]):
            return  # avoid logging
        # case handling

        # Timeout error with view :)
        if isinstance(
            error,
            (
                TimeoutError,
                asyncio.exceptions.TimeoutError,
            ),
        ):
            # add a little button that show a command expired
            await view_timeout(Interaction)
            return  # avoid logging
        # We mostly ignore command on CommandOnCooldown
        if isinstance(error, errors.CommandOnCooldown):
            embed = disnake.Embed(
                title=f"This command has a cooldown, try in {int(error.retry_after)}s"
            )
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # Missing Permission error from bot
        if isinstance(error, disnake.errors.Forbidden):
            embed = disnake.Embed(
                title="Error",
                description="The bot does not have the required permissions to execute this command.",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            embed.add_field(
                name="Permission Error",
                value="The bot lacks the necessary permissions to perform this action.",
            )
            embed.set_footer(text="Please check the bot's permissions and try again.")
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # Missing Permission error from user
        if isinstance(error, errors.MissingPermissions):
            embed = disnake.Embed(
                title="Error",
                description="You do not have the required permissions to execute this command.",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            embed.set_footer(text="Please check your permissions and try again.")
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # if someone doesn't give all the command argument
        if isinstance(error, errors.MissingRequiredArgument):
            embed = disnake.Embed(
                title="Error",
                description="Missing required arguments for this command.",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            embed.set_footer(text="Please provide all required arguments and try again.")
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # if the arrow command was used more than one time
        if isinstance(error, errors.MaxConcurrencyReached):
            embed = disnake.Embed(
                title="Error",
                description=f"Command '{command.qualified_name}' is already in use. Please wait for it to complete before using it again.",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            embed.set_footer(text="Please wait for the current command to finish.")
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # if the top.gg server are dead.
        if isinstance(error, (topgg.errors.ServerError, topgg.errors.HTTPException)):
            embed = disnake.Embed(
                title="Error",
                description="An error occurred while communicating with the Top.gg API.",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            embed.set_footer(text="Please try again later.")
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # bad embed form
        if isinstance(error, disnake.errors.HTTPException):
            embed = disnake.Embed(
                title="Error",
                description="An error occurred while sending an embed message.",
                color=disnake.Color.red(),
            )
            embed.set_thumbnail(
                url="https://media.singularityapp.online/images/assets/pfpsister.png"
            )
            embed.set_footer(text="Please try again.")
            await self.try_sending_message(Interaction, embed)
            return  # avoid logging
        # log the error and warn
        warning(f'In the "{command}" command got the Exception: {str(type(error))}')
        await self.logger(command, error)

    # try sending a message without an error
    async def try_sending_message(
        self, Interaction: disnake.ApplicationCommandInteraction, embed: disnake.Embed
    ) -> None:
        try:
            await Interaction.response.send_message(embed=embed)
        except Exception as e:
            if isinstance(e, disnake.errors.InteractionResponded):
                try:
                    await Interaction.followup.send(embed=embed)
                except:
                    await Interaction.send(embed=embed)
                return
            await Interaction.send(embed=embed)

    # log a given error
    async def logger(
        self,
        Interaction_command: commands.InvokableApplicationCommand,
        error: Exception,
    ) -> None:
        try:
            # from stack overflow : https://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
            error_traceback = "".join(
                traceback.format_exception(
                    type(error), error, error.__traceback__
                )
            )
            # log the error
            await self.singularitybot.database.add_log(
                datetime.now(),
                str(Interaction_command.qualified_name),
                str(type(error)),
                error_traceback,
            )
        except:
            warning(f"Failed Logging! Is the database compromised?")


def setup(client: SingularityBot):
    client.add_cog(ErrorHandle(client))
