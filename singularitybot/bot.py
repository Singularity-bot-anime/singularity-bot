import os
import disnake
import asyncio

from singularitybot.models.bot.singularitybot import SingularityBot
from disnake.ext import commands

LOOP = asyncio.get_event_loop()
TOKEN = os.environ["DISCORD_KEY_SINGULARITY"]

textart = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⡴⠶⠞⠛⠛⠉⠉⠉⠉⠉⠉⠛⠛⠶⢦⣄⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣶⣾⠿⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠈⠛⢦⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⢛⣩⠶⠛⠉⠀⠀⠀⣀⣤⡴⠶⠚⠛⠛⠛⠉⠛⠛⠛⢶⡟⠉⢻⡄⠀⠀⠀⠈⢻⡄
⠀⠀⠀⠀⠀⠀⠀⣠⡴⠟⢉⣠⠶⠋⠁⠀⠀⣠⡴⠞⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠷⡤⠾⣇⠀⠀⠀⠀⠀⣿
⠀⠀⠀⠀⣠⡴⠛⠁⣀⡴⠛⠁⠀⢀⣠⠶⠛⠁⠀⠀⠀⣀⣠⡤⠶⠒⠛⠛⠛⠛⠛⠶⣤⡀⠀⠀⠀⢹⡆⠀⠀⠀⠀⢸
⠀⢀⣴⠟⠁⠀⣠⡾⠋⠀⠀⢀⡴⠛⠁⠀⢰⠞⠳⡶⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⠀⠀⢈⡇⠀⠀⠀⠀⣾
⢴⠟⠁⠀⢀⡼⠋⠀⠀⢀⡴⠋⠀⠀⠀⣠⡾⠷⠶⠇⢀⣠⣤⠶⠖⠲⢶⣄⠀⠀⠀⠀⠀⡿⠀⠀⠀⢸⡇⠀⠀⠀⢰⡏
⠀⠀⠀⣰⠟⠀⠀⠀⣴⠏⠀⠀⠀⣠⠞⠉⠀⠀⣠⡶⠋⠁⠀⠀⠀⠀⢀⡿⠀⠀⠀⠀⣼⠃⠀⠀⢀⡟⠂⠀⠀⢠⡟⠀
⠀⢀⣼⠋⠀⠀⢀⡾⠁⠀⠀⢠⡞⠁⠀⠀⢠⡾⠁⠀⠀⠀⠀⣀⣀⣠⡾⠁⠀⠀⣠⡾⠁⠀⠀⢠⡞⠁⠀⠀⣰⠟⠀⠀
⠀⣾⠃⠀⢠⡟⠛⣷⠂⠀⢠⡟⠀⠀⠀⠀⢾⡀⠀⠀⠀⠀⣸⣏⣹⡏⠀⠀⣠⡾⠋⠀⠀⢀⣴⠏⠀⠀⢀⡼⠋⠀⠀⠀
⣸⠇⠀⠀⠈⢻⡶⠛⠀⠀⣿⠀⠀⠀⠀⠀⠈⠛⠲⠖⠚⠋⠉⠉⠉⣀⣤⠞⠋⠀⠀⢀⣴⠟⠁⠀⠀⣰⠟⠁⠀⣴⠆⠀
⣿⠀⠀⠀⠀⢸⡇⠀⠀⠀⢻⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⠛⠉⣀⣀⡀⣀⡴⠟⠁⠀⢀⣤⠞⠁⢀⣴⠟⠁⠀⠀
⣿⠀⠀⠀⠀⠘⣧⠀⠀⠀⠀⠙⠳⠶⠤⣤⠤⠶⠶⠚⠋⠉⠀⠀⠀⡟⠉⠈⢻⡏⠀⠀⣀⡴⠛⠁⣠⡶⠋⠁⠀⠀⠀⠀
⢻⡀⠀⠀⠀⠀⠘⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⠶⠻⢦⣤⠟⣀⣤⠞⢋⣠⡴⠛⠁⠀⠀⠀⠀⠀⠀⠀
⠈⢿⣄⠀⠀⠀⠀⠀⠈⠛⠳⠶⠤⠤⠤⠤⠤⠴⠶⠒⠛⠉⠁⠀⠀⢀⣠⡴⣞⣋⣤⠶⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠙⢷⡶⠛⠳⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣾⠿⠿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠘⣧⡀⣀⣿⠦⣤⣤⣤⣤⣤⣤⠤⠶⠶⠞⠛⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

"""

Client = SingularityBot(loop=LOOP,debug=True)

print("All the databases ,emojis and apis have been initialized")

main_extension = {
    "extensions.admincommands",
    "extensions.utils",
    "extensions.gacha",
    "extensions.adventure",
    "extensions.items",
    "extensions.management",
    "extensions.fight",
    "extensions.wormhole"
}


# loads file and stuff
for file in main_extension:
    try:
        Client.load_extension(file)
    except commands.ExtensionAlreadyLoaded:
        # print(f'{file} already loaded , ignoring')
        pass
    else:
        print(f"loaded {file}")


@Client.event
async def on_shard_ready(shard_id: int):
    Client.shard_id = shard_id
    Client.start_fight_listeners()
    if shard_id == 0:
        Client.start_fight_handler()
        Client.start_matchmaking()
    print(f"Shard id:{shard_id} is ready")


@Client.event
async def on_ready():
    print(f"The bot is ready")
    print(textart)

    await Client.change_presence(activity=disnake.Game(f"Singularity converging"))


if __name__ == "__main__":
    # run the bot
    Client.run(TOKEN)