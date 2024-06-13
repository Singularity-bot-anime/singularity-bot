import random


from typing import TYPE_CHECKING, List


from singularitybot.models.gameobjects.effects import Effect, EffectType

# It's for typehint
if TYPE_CHECKING:
    from singularitybot.models.gameobjects.character import Character


def get_payload():
    return {}


"""

name your fonction to the character

def special_boiler_plate(character:"character",allied_character:List["character"],ennemy_character:List["character"])->tuple:
    payload = get_payload()
    #Whatever your code does to the lists above
    #Payload Contain behavior change to the game
    #message is what should be printed to the embed
    return payload,message

their is a load of exemple bellow
AOE attack : 
AOE effect : 
self buff  : 

"""

def not_implemented(
    character: "Character",
    allied_character: List["Character"],
    ennemy_character: List["Character"],
) -> tuple:
    payload = get_payload()
    message = f"｢{character.name}｣ has no power yet"
    payload["is_a_special"] = False
    return payload, message


specials = {}
