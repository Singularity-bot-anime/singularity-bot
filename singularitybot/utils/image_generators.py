import io
import disnake

from PIL import Image, ImageDraw,ImageFont
from singularitybot.models.database.user import User

FONT = "singularitybot/data/assets/sonoma2.otf"
def get_error_file() -> disnake.File:
    """Returns the default error image"""
    return disnake.File("singularitybot/data/assets/errorloading.jpg")


async def get_profile_image(user:User) -> disnake.File:
    #try:
        image = Image.open("singularitybot/data/assets/profile_template.png")
        # create object for drawing
        AVATAR_SIZE = 128

        # get both avatars
        avatar1 = user.discord.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image1 = Image.open(buffer_avatar1)
        # create a 200s*200 round display_avatar
        avatar_image1 = avatar_image1.resize((200, 200))
        # make the image a circle

        circle_image = Image.new("L", (200, 200))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, 200, 200), fill=255)

        image.paste(avatar_image1, (21,21), circle_image)
        draw = ImageDraw.Draw(image)
        text = user.discord.display_name
        font = ImageFont.truetype(FONT, 40)
        color = "white"
        position = (360, 80)
        draw.text(position, text, fill=color, font=font)
        text = str(user.level)
        font = ImageFont.truetype(FONT, 40)
        color = "white"
        position = (360, 150)
        draw.text(position, text, fill=color, font=font)
        text = f"{str(user.energy)}/{str(user.total_energy)}⚡"
        font = ImageFont.truetype(FONT, 40)
        color = "white"
        position = (360, 210)
        draw.text(position, text, fill=color, font=font)
        text = str(user.galaxy_id)
        font = ImageFont.truetype(FONT, 20)
        color = "white"
        position = (65, 300)
        draw.text(position, text, fill=color, font=font)
        text = str(user.fragments)
        font = ImageFont.truetype(FONT, 20)
        color = "white"
        position = (250, 300)
        draw.text(position, text, fill=color, font=font)
        text = str(user.super_fragements)
        font = ImageFont.truetype(FONT, 20)
        color = "white"
        position = (425, 300)
        draw.text(position, text, fill=color, font=font)
        text = str(0)
        font = ImageFont.truetype(FONT, 20)
        color = "white"
        position = (65, 410)
        draw.text(position, text, fill=color, font=font)
        text = str(None)
        font = ImageFont.truetype(FONT, 20)
        color = "white"
        position = (250, 410)
        draw.text(position, text, fill=color, font=font)
        text = str("No")
        font = ImageFont.truetype(FONT, 20)
        color = "white"
        position = (425, 410)
        draw.text(position, text, fill=color, font=font)
        
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "myimage.png")
    #except:
        #file = get_error_file()
        return file

    

async def origins_tower_image(user: disnake.User, stage: int) -> disnake.File:
    try:
        image = Image.open("singularitybot/data/assets/tower_1.png")
        # create object for drawing
        AVATAR_SIZE = 128

        # get both avatars
        avatar1 = user.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image1 = Image.open(buffer_avatar1)
        # create a 200s*200 round display_avatar
        avatar_image1 = avatar_image1.resize((AVATAR_SIZE, AVATAR_SIZE))
        # make the image a circle

        circle_image = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        # stage
        if stage == 1:
            pos = (814,1598)
        if stage == 2:
            pos = (814,1379)
        if stage == 3:
            pos = (814,1158)
        if stage == 4:
            pos = (814,940)
        if stage == 5:
            pos = (814,715)
        if stage == 6:
            pos = (814,496)
        if stage == 7:
            pos = (814,277)
        if stage == 8:
            pos = (814,60)
        pos = list(pos)
        # paste the result
        image.paste(avatar_image1, pos, circle_image)
        # create buffer
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "myimage.png")
    except Exception as e:
        file = get_error_file()
        raise(e)
    return file


async def get_part_4_tower_image(user: disnake.User, stage: int) -> disnake.File:
    try:
        image = Image.open("stfubot/data/image/towertemplate_part4.png")
        # create object for drawing
        AVATAR_SIZE = 256

        # get both avatars
        avatar1 = user.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image1 = Image.open(buffer_avatar1)
        # create a 200s*200 round display_avatar
        avatar_image1 = avatar_image1.resize((AVATAR_SIZE, AVATAR_SIZE))
        # make the image a circle

        circle_image = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        # stage
        if stage == 1:
            pos = (1780 - AVATAR_SIZE // 2, 200 - AVATAR_SIZE // 2)
        if stage == 2:
            pos = (1560 - AVATAR_SIZE // 2, 840 - AVATAR_SIZE // 2)
        if stage == 3:
            pos = (940 - AVATAR_SIZE // 2, 1200 - AVATAR_SIZE // 2)
        if stage == 4:
            pos = (460 - AVATAR_SIZE // 2, 751 - AVATAR_SIZE // 2)
        if stage == 5:
            pos = (787 - AVATAR_SIZE // 2, 476 - AVATAR_SIZE // 2)
        image.paste(avatar_image1, pos, circle_image)
        # create buffer
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "myimage.png")
    except:
        file = get_error_file()
    return file


async def get_part_5_tower_image(user: disnake.User, stage: int) -> disnake.File:
    try:
        image = Image.open("stfubot/data/image/towertemplate_part5.png")
        # create object for drawing
        AVATAR_SIZE = 128

        # get both avatars
        avatar1 = user.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image1 = Image.open(buffer_avatar1)
        # create a 200s*200 round display_avatar
        avatar_image1 = avatar_image1.resize((AVATAR_SIZE, AVATAR_SIZE))
        # make the image a circle

        circle_image = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        # stage
        if stage == 1:
            pos = (585 - AVATAR_SIZE // 2, 555 - AVATAR_SIZE // 2)
        if stage == 2:
            pos = (504 - AVATAR_SIZE // 2, 785 - AVATAR_SIZE // 2)
        if stage == 3:
            pos = (300 - AVATAR_SIZE // 2, 500 - AVATAR_SIZE // 2)
        if stage == 4:
            pos = (583 - AVATAR_SIZE // 2, 200 - AVATAR_SIZE // 2)
        if stage == 5:
            pos = (540 - AVATAR_SIZE // 2, 413 - AVATAR_SIZE // 2)
        image.paste(avatar_image1, pos, circle_image)
        # create buffer
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "myimage.png")
    except:
        file = get_error_file()
    return file


async def get_tower_victory_image(user: disnake.User) -> disnake.File:
    try:
        image = Image.open("stfubot/data/image/finalbattleview.png")
        # create object for drawing
        AVATAR_SIZE = 128
        # get both avatars
        avatar1 = user.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image1 = Image.open(buffer_avatar1)
        # create a 128*128 round display_avatar
        avatar_image1 = avatar_image1.resize((AVATAR_SIZE, AVATAR_SIZE))
        # make the image a circle

        circle_image = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        # paste the result
        image.paste(avatar_image1, (125, 30), circle_image)
        # create buffer
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "myimage.png")
    except:
        file = get_error_file()
    return file


# easier to retrive programmatically
tower_images = {
    "1": origins_tower_image,
    "2": get_part_4_tower_image,
    "3": get_part_5_tower_image,
}

# this returns a image used for fight
async def get_win_image(user1: disnake.User) -> disnake.File:
    try:
        image = Image.open("singularitybot/data/assets/tower_1.png")
        # create object for drawing
        AVATAR_SIZE = 128
        # get both avatars
        avatar1 = user1.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        avatar_image1 = Image.open(buffer_avatar1)
        # create a 128*128 round display_avatar
        avatar_image1 = avatar_image1.resize((240, 240))
        # make the image a circle

        circle_image = Image.new("L", (240, 240))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, 240, 240), fill=255)
        # paste the result
        image.paste(avatar_image1, (180, 180), circle_image)
        # create buffer
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "image.png")
    except:
        file = get_error_file()
    return file


# this returns a image used for fight
async def get_fight_image(user1: disnake.User, user2: disnake.User,ranked=False) -> disnake.File:
    try:
        if ranked:
            fight="ranked_"
        else:
            fight = ""
        image = Image.open(f"singularitybot/data/assets/fight_{fight}image.png")
        # create object for drawing
        AVATAR_SIZE = 128
        # get both avatars
        avatar1 = user1.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        avatar2 = user2.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar1 = io.BytesIO(await avatar1.read())
        buffer_avatar2 = io.BytesIO(await avatar2.read())
        avatar_image1 = Image.open(buffer_avatar1)
        avatar_image2 = Image.open(buffer_avatar2)
        # create a 128*128 round display_avatar
        avatar_image1 = avatar_image1.resize((260, 260))
        avatar_image2 = avatar_image2.resize((260, 260))
        # make the image a circle

        circle_image = Image.new("L", (260, 260))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, 260, 260), fill=255)
        # paste the result
        image.paste(avatar_image1, (39, 170), circle_image)
        image.paste(avatar_image2, (602, 170), circle_image)
        # create buffer
        buffer_output = io.BytesIO()
        # save PNG in buffer
        image.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        # give the file
        file = disnake.File(buffer_output, "image.png")
    except:
        file = get_error_file()
    return file
