import json

from singularitybot.models.gameobjects.itemabilities import item_specials

with open(
    "singularitybot/data/templates/items.json", "r", encoding="utf-8"
) as item:
    item_file = json.load(item)["items"]


class Item:
    """This interface to jsoned data THIS CLASS IS NOT INTENDED TO BE CREATED MANUALLY
    Or to be modified.
    """

    def __init__(self, data: dict):

        self.data: dict = data
        self.id: int = data["id"]
        self.name: str = item_file[self.id-1]["name"]
        self.bonus_hp: int = item_file[self.id-1]["bonus_hp"]
        self.bonus_damage: int = item_file[self.id-1]["bonus_damage"]
        self.bonus_speed: int = item_file[self.id-1]["bonus_speed"]
        self.bonus_critical: int = item_file[self.id-1]["bonus_critical"]
        self.bonus_armor:int = item_file[self.id-1]["bonus_armor"]
        self.price: int = item_file[self.id-1]["price"]
        self.prurchasable: bool = item_file[self.id-1]["prurchasable"]
        self.emoji = item_file[self.id-1]["emoji"]
        self.is_equipable = item_file[self.id-1]["is_equipable"]
        self.is_active = item_file[self.id-1]["is_active"]
        self.is_usable = item_file[self.id-1]["is_usable"]
        self.turn_for_ability = item_file[self.id-1]["turn_for_ability"]
        self.special_image = item_file[self.id-1]["special_image"]
        # Variable
        self.special_meter: int = 0

    def to_dict(self):
        return self.data

    def special(self, stand, allies, ennemies) -> str:
        self.special_meter = 0
        try:
            message = item_specials[f"{self.id}"](stand, allies, ennemies)
        except Exception as e:
            raise(e)
            message = "None"
        return message

    def as_special(self):
        return self.is_active and self.special_meter >= self.turn_for_ability


def item_from_dict(data: dict) -> Item:
    """take a dict and return an Item object

    Args:
        data (dict): normalized data

    Returns:
        Item: Item class
    """
    return Item(data)


def get_item_from_template(template: dict) -> dict:
    return {"id": template["id"]}
