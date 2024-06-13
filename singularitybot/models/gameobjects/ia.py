import disnake

from typing import List

from singularitybot.models.gameobjects.character import Character, character_from_dict


class Ia:
    def __init__(self, data: dict):
        self.avatar = data["avatar"]

        class d:
            def __init__(self, name: str):
                self.name: str = name

        self.discord = d(data["name"])
        self.main_characters: List[Character] = [
            character_from_dict(s) for s in data["main_characters"]
        ]
        self.id = "0101"
        self.message: disnake.Message = None
        self.is_human = False

    def choice(self, ennemies: List[Character]):
        # What the Ia must prioritize
        def prio(x: Character):
            return x.current_hp * (x.current_damage) / x.current_armor

        ennemies.sort(key=prio, reverse=True)
        return ennemies[0]
