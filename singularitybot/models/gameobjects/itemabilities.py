import random

from typing import TYPE_CHECKING, List

from singularitybot.models.gameobjects.effects import Effect, EffectType

# It's for typehint
if TYPE_CHECKING:
    from singularitybot.models.gameobjects.character import Character


"""

name your fonction to the character

def item_special_boiler_plate(character:"character",allied_character:List["character"],ennemy_characterd:List["character"])->tuple:
    #Whatever your code does to the lists above
    #Payload Contain behavior change to the game
    #message is what should be printed to the embed
    return message


"""

def explosive_tag(
    character: "Character", allied_character: List["Character"], ennemy_character: List["Character"]
) -> tuple:
    multiplier = 30
    valid_character = [i for i in ennemy_character if i.is_alive()]
    if len(valid_character) != 0:
        target = random.choice(valid_character)
        target.current_hp -= multiplier
        message = f"｢{character.name}｣'s Sheer heart attack explode on {target.name} for {multiplier} damage"
    message = f"Sheer heart attack schearch for ennemies"
    return message



item_specials = {
    "4":explosive_tag
}