import disnake

from typing import List

from singularitybot.models.gameobjects.character import Character, character_from_dict


class Ia:
    def __init__(self, data: dict):
        self.data = data
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
        # Filter only alive enemies and keep their original indices
        alive_ennemies = [(index, enemy) for index, enemy in enumerate(ennemies) if enemy.is_alive()]

        # Sort enemies based on taunt status, then by damage, then by HP
        def prio(x):
            return (
                not x[1].taunt,      # False if x has taunt, True otherwise (False is prioritized over True)
                -x[1].current_damage, # Higher damage is prioritized
                -x[1].current_hp      # Higher HP is prioritized
            )

        alive_ennemies.sort(key=prio)
        return alive_ennemies[0][0] if alive_ennemies else 0

