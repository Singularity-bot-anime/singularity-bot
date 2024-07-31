from PIL import Image, ImageDraw, ImageFont
import json
import disnake
import os
import io

class Map:
    def __init__(self, map_image_path, map_data_path):
        self.map_image = Image.open(map_image_path).convert("RGBA")
        with open(map_data_path) as f:
            self.map_data = json.load(f)
        self.size = self.map_data['size']
        self.start_tile = self.map_data['map_start_tile']
        self.tile_size = self.map_data['tile_size']
        self.collision = self.map_data['collision']
        self.triggers = self.map_data['triggers']
        self.next_level = self.map_data['next_level']
        self.triggered = set()  # To track triggered events

        self.t_data = self.map_data['t_data']
        self.player_start_position = self.map_data['start_tile']
        self.player_position = self.player_start_position

    def is_valid_move(self, x, y):
        if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
            return False
        tile_index = y * self.size[0] + x
        return self.collision[tile_index] == 0

    def move_player(self, direction):
        x, y = self.player_position
        if direction == "up":
            y -= 1
        elif direction == "down":
            y += 1
        elif direction == "left":
            x -= 1
        elif direction == "right":
            x += 1
        if self.is_valid_move(x, y):
            self.player_position = (x, y)
            return True
        return False

    def get_allowed_moves(self):
        """Get a list of allowed move directions."""
        allowed_moves = []
        x, y = self.player_position
        if self.is_valid_move(x, y - 1):
            allowed_moves.append("up")
        if self.is_valid_move(x, y + 1):
            allowed_moves.append("down")
        if self.is_valid_move(x - 1, y):
            allowed_moves.append("left")
        if self.is_valid_move(x + 1, y):
            allowed_moves.append("right")
        return allowed_moves

    def trigger_event(self):
        x, y = self.player_position
        key = f"{x}:{y}"
        if key in self.triggers and key not in self.triggered:
            self.triggered.add(key)
            return self.triggers[key],self.t_data[key]
        return None

    def render_map_with_avatar(self, discord_avatar):
        map_copy = self.map_image.copy()
        avatar = discord_avatar
        avatar_x, avatar_y = self.player_position
        pos_x = (avatar_x * self.tile_size) + self.start_tile[0]
        pos_y = (avatar_y * self.tile_size) + self.start_tile[1]
        map_copy.paste(avatar, (pos_x, pos_y), avatar)
        map_copy = map_copy.resize((600,600))
        buffer_output = io.BytesIO()
        # save PNG in buffer
        map_copy.save(buffer_output, format="PNG")
        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)
        file = disnake.File(buffer_output, "myimage.png")
        return file
