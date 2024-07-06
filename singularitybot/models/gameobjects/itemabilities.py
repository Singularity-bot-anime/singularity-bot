import random

from typing import TYPE_CHECKING, List

from singularitybot.models.gameobjects.effects import Effect, EffectType,NEGATIVE_EFFECTS

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
        message = f"｢{character.name}｣'s explosive tag detonage on {target.name} for {multiplier} damage"
    message = f"explosive tag detonage"
    return message

def mahoraga_wheel(
    character: "Character", allied_character: List["Character"], ennemy_character: List["Character"]
) -> tuple:
   
    character.effects = [e for e in character.effects if not e.type in NEGATIVE_EFFECTS]
    if character.current_speed < character.start_speed:
        character.current_speed = character.start_speed
    if character.current_armor < character.start_armor:
        character.current_armor = character.start_armor
    
    message = f"The wheel adapts to the effects and clear them off {character.name}"

    return message

item_specials = {
    "4":explosive_tag,
    "7":mahoraga_wheel,
}