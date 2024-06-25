import io
import disnake

from PIL import Image, ImageDraw,ImageFont
from singularitybot.models.database.user import User

FONT = "singularitybot/data/assets/sonoma2.otf"
def get_error_file() -> disnake.File:
    """Returns the default error image"""
    return disnake.File("singularitybot/data/assets/errorloading.jpg")


async def get_profile_image(user: User, client) -> disnake.File:
    try:
        image = Image.open("singularitybot/data/assets/profile_template.png")
        AVATAR_SIZE = 128

        # User avatar
        avatar_url = user.discord.display_avatar.with_format("jpg").with_size(AVATAR_SIZE)
        buffer_avatar = io.BytesIO(await avatar_url.read())
        avatar_image = Image.open(buffer_avatar).resize((200, 200))
        circle_mask = Image.new("L", (200, 200))
        circle_draw = ImageDraw.Draw(circle_mask)
        circle_draw.ellipse((0, 0, 200, 200), fill=255)
        image.paste(avatar_image, (21, 21), circle_mask)

        # Draw text fields
        draw = ImageDraw.Draw(image)
        font_large = ImageFont.truetype(FONT, 40)
        font_medium = ImageFont.truetype(FONT, 20)
        font_small = ImageFont.truetype(FONT, 10)
        color = "white"

        draw.text((360, 80), user.discord.display_name, fill=color, font=font_large)
        draw.text((360, 150), str(user.level), fill=color, font=font_large)
        draw.text((360, 210), f"{user.energy}/{user.total_energy}⚡", fill=color, font=font_large)
        galaxy_name = "Not part of a galaxy" if not user.galaxy_id else (await client.database.get_galaxy_info(user.galaxy_id)).name
        draw.text((65, 300), galaxy_name, fill=color, font=font_small)
        draw.text((250, 300), str(user.fragments), fill=color, font=font_medium)
        draw.text((425, 300), str(user.super_fragements), fill=color, font=font_medium)
        draw.text((65, 410), str(0), fill=color, font=font_medium)
        draw.text((250, 410), str(None), fill=color, font=font_medium)
        draw.text((425, 410), "yes" if user.is_donator() else "no", fill=color, font=font_medium)

        # Add main characters to the profile image
        main_characters = user.main_characters[:3]  # Assuming user.main_characters returns the top 3 characters
        char_size = 128  # Square size of each character image
        char_positions = [
            (28+i*200, 450)
            for i in range(3)
        ]

        for char, pos in zip(main_characters, char_positions):
            char_image = await client.database.get_character_image(char.id)
            char_image = char_image.resize((char_size, char_size)).convert("RGBA")
            char_mask = Image.new("L", (char_size, char_size), 255)
            image.paste(char_image, pos, char_image)

        buffer_output = io.BytesIO()
        image.save(buffer_output, format="PNG")
        buffer_output.seek(0)
        return disnake.File(buffer_output, "profile.png")
    except Exception as e:
        print(f"Error generating profile image: {e}")
        return get_error_file()


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
    return file

# easier to retrive programmatically
tower_images = {
    "1": origins_tower_image
}

# this returns a image used for fight
async def get_win_image(user1: disnake.User) -> disnake.File:
    try:
        image = Image.open("singularitybot/data/assets/fight_win_image.png")
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
