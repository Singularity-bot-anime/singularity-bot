import random
import math
import json
import enum

from singularitybot.models.gameobjects.items import Item, item_from_dict
from singularitybot.models.gameobjects.effects import Effect, EffectType
from singularitybot.models.gameobjects.characterabilities import (
    specials,
    not_implemented,
)
from typing import List, TypeVar


HPSCALING = 5
DAMAGESCALING = 1
SPEEDSCALING = 1
CRITICALSCALING = 1
CRITMULTIPLIER = 1
DODGENERF = 1
STXPTOLEVEL = 100
MAX_LEVEL = 100
LEVEL_TO_STAT_INCREASE = 1

character = TypeVar("character", bound="Character")


class Character:
    def __init__(self, data: dict):
        with open("singularitybot/data/templates/characters.json", "r") as item:
            character_file = json.load(item)["characters"]
        # define the constant
        self.data: dict = data
        self.id: str = data["id"]
        self.name: str = character_file[self.id-1]["name"]
        self.rarity:str = character_file[self.id-1]["rarity"]
        self.xp: int = data["xp"]
        self.awaken: int = data["awaken"]
        self.types:list[str] = data["types"]
        self.qualities:list[str] = data["qualities"]
        self.etypes:list[Types] = [Types.from_string(typ) for typ in self.types]
        self.equalities:list[Qualities] = [Qualities.from_string(qual) for qual in self.qualities]
        self.base_critical: float = character_file[self.id-1]["base_critical"]
        self.base_hp: int = character_file[self.id-1]["base_hp"]
        self.base_damage: int = character_file[self.id-1]["base_damage"]
        self.base_speed: int = character_file[self.id-1]["base_speed"]
        self.base_armor: int = character_file[self.id-1]["armor"]
        self.turn_for_ability: int = character_file[self.id-1]["turn_for_ability"]
        self.special_description: str = character_file[self.id-1]["special_description"]
        self.special_url:str = character_file[self.id-1]["special_url"]
        self.taunt: bool = character_file[self.id-1]["taunt"]
        self.items: List[Item] = [item_from_dict(s) for s in data["items"]]
        self.universe: str = character_file[self.id-1]["universe"]
        self.level: int = min(MAX_LEVEL, self.xp // STXPTOLEVEL)

        # Compute the starting Items and XP scaling.
        bonus_hp = (100 * self.taunt) * 100 # Give taunting characters more effective health
        bonus_damage = 0
        bonus_speed = 0
        bonus_critical = 0
        bonus_armor = (100 * self.taunt) # Give taunting characters more effective health
        for item in self.items:
            bonus_hp += item.bonus_hp
            bonus_damage += item.bonus_damage
            bonus_speed += item.bonus_speed
            bonus_critical += item.bonus_critical
            bonus_armor += item.bonus_armor
        # LEVEL SCALING
        bonus_damage += (
            (self.level // LEVEL_TO_STAT_INCREASE)
            * self.base_damage
            * (DAMAGESCALING / 100)
        )
        bonus_hp += (
            (self.level // LEVEL_TO_STAT_INCREASE)
            * self.base_hp
            * (HPSCALING / 100)
        )
        bonus_speed += (
            (self.level // LEVEL_TO_STAT_INCREASE)
            * self.base_speed
            * (SPEEDSCALING / 100)
        )
        bonus_critical += (
            (self.level // LEVEL_TO_STAT_INCREASE)
            * self.base_critical
            * (CRITICALSCALING / 100)
        )

        # Define the starting STATS and variables
        self.current_hp = int(self.base_hp + bonus_hp * (1 + self.awaken / 3))
        self.current_damage = int(
            self.base_damage + bonus_damage * (1 + self.awaken / 3)
        )
        self.current_speed = int(self.base_speed + bonus_speed * (1 + self.awaken / 3))
        self.current_critical = self.base_critical + bonus_critical * (
            1 + self.awaken / 3
        )
        self.current_armor = int(self.base_armor + bonus_armor * (1 + self.awaken / 3))
        
        #TYPE and qualities final multiplier
        
        for type_,quality in zip(self.types,self.qualities):
            type_ = Types.from_string(type_)
            quality = Qualities.from_string(quality)
            if type_ == Types.ATTACK:
                self.current_damage *= quality.coef
            elif type_ == Types.BALANCE:
                self.current_armor *= (quality.coef ** 0.25)
                self.current_damage *= (quality.coef ** 0.25)
                self.current_speed *= (quality.coef ** 0.25)
                self.current_critical *= (quality.coef ** 0.25)
            elif type_ == Types.DEFENSE:
                self.current_armor *= quality.coef
            elif type_ == Types.LUCK:
                self.current_critical *= quality.coef
        
        self.start_hp = self.current_hp
        self.start_damage = self.current_damage
        self.start_speed = self.current_speed
        self.start_critical = self.current_critical
        self.start_armor = self.current_armor
        self.effects: List[Effect] = []
        self.special_meter: int = 0
        self.turn: int = 0
        self.armor: int = 1

    def is_alive(self) -> bool:
        """Check if a character is alive

        Returns:
            bool: The  answer
        """
        if self.current_hp <= 0:
            self.current_hp = 0
        return self.current_hp > 0

    def attack(self, ennemy_character: character, multiplier: int = 1) -> dict:
        """Attack a character

        Args:
            ennemy_character (character): the character to attack

        Returns:
            dict: Default {"damage": 0, "critical": False, "dodged": False}
        """
        # create a return dict this time :)
        atck = {"damage": 0, "critical": False, "dodged": False}
        crit = random.randint(0, 100)
        # classic attack have no modifiers so x1
        multi = multiplier
        if self.current_critical >= crit:
            multi *= CRITMULTIPLIER
            atck["critical"] = True
        dodge_roll = False
        # armor reduction calculation
        dmg_reduction = (ennemy_character.current_armor +100)/(2* ennemy_character.current_armor)
        # dmg reduction is capped at 10
        dmg_reduction = min(10,dmg_reduction)
        # we apply the dmg reduction
        multi *= dmg_reduction
        # If the ennemy is faster check if he dodged
        if ennemy_character.current_speed > self.current_speed:
            dodge_roll = (
                random.randint(0, 100)
                < (ennemy_character.current_speed - self.current_speed) // DODGENERF
            )
            atck["dodged"] = dodge_roll
        # if it is dodged the we do not compute damage
        if dodge_roll:
            return atck
        damage = int(
            self.current_damage * multi
        )
        ennemy_character.current_hp -= damage
        atck["damage"] = damage
        return atck

    def is_stunned(self) -> bool:
        """Check if the character is stunned

        Returns:
            bool: whether the character is stunned
        """
        return EffectType.STUN in [e.type for e in self.effects]

    def end_turn(self) -> None:
        """Make the relevant action at the end of the turn"""
        # Apply effects
        for effect in self.effects:
            if effect.duration <= 0:
                continue
            if effect.type in [EffectType.POISON, EffectType.BLEED, EffectType.BURN]:
                self.current_hp -= effect.value
            elif effect.type == EffectType.WEAKEN and not effect.used:
                self.current_damage -= effect.value
            elif effect.type == EffectType.REGENERATION:
                self.current_hp = min(self.current_hp + effect.value, self.start_hp)
            elif effect.type == EffectType.SLOW and not effect.used:
                self.current_speed -= effect.value
            elif effect.type == EffectType.HEALTHBOOST and not effect.used:
                self.current_hp += effect.value
            elif effect.type == EffectType.DAMAGEUP and not effect.used:
                self.current_damage += effect.value
            effect.duration -= 1
            if not effect.used:
                effect.used = True

        # Cleanup effects that have ended and restore original state
        remaining_effects = []
        for effect in self.effects:
            if effect.duration > 0:
                remaining_effects.append(effect)
            else:
                if effect.type == EffectType.HEALTHBOOST:
                    self.current_hp = max(self.current_hp - effect.value, 1)
                elif effect.type == EffectType.DAMAGEUP:
                    self.current_damage -= max(self.current_damage - effect.value, 1)
                elif effect.type == EffectType.WEAKEN:
                    self.current_armor += max(self.current_armor - effect.value, 1)
                elif effect.type == EffectType.SLOW:
                    self.current_speed += max(self.current_speed - effect.value, 1)

        self.effects = remaining_effects

        # Add to the special meter
        self.special_meter += 1
        self.turn += 1

        # Add to items' special meter
        for item in self.items:
            item.special_meter += 1

    def as_special(self) -> bool:
        return self.special_meter >= self.turn_for_ability

    def special(self, allies: List[character], ennemies: List[character]) -> tuple:
        """used for fight

        Args:
            allies (List[character]): list of allies
            ennemies (List[character]): list of ennemies

        Returns:
            tuple: payload,message
        """
        # reset the meter
        self.special_meter = 0
        special_func = specials.get(str(self.id), not_implemented)
        return special_func(self, allies, ennemies)

    def to_dict(self) -> dict:
        """Update the data of the character

        Returns:
            dict: the data of the character
        """
        self.data["xp"] = self.xp
        self.data["awaken"] = self.awaken
        self.data["items"] = [s.to_dict() for s in self.items]
        self.data["types"] = self.types
        self.data["qualities"] = self.qualities
        return self.data

    def reset(self) -> None:
        """call at the end of a fight"""
        self.data["xp"] = self.xp
        self.data["awaken"] = self.awaken
        self.data["items"] = [s.to_dict() for s in self.items]
        self.__init__(self.data)


def character_from_dict(data: dict) -> Character:
    return Character(data)


def get_character_from_template(template: dict,types:list[str],qualities:list[str]) -> Character:
    data = {"id": template["id"], "xp": 0, "awaken": 0,"types":types,"qualities":qualities ,"items": []}
    return Character(data)


class Types(enum.Enum):
    ATTACK = ("ATTACK", "⚔️", 1)
    DEFENSE = ("DEFENSE", "🛡️", 2)
    SPEED = ("SPEED", "💨", 3)
    LUCK = ("LUCK", "🍀", 4)
    BALANCE = ("BALANCE", "⚖️", 5)

    def __new__(cls, string, emoji, number):
        obj = object.__new__(cls)
        obj._value_ = string
        obj.emoji = emoji
        obj.number = number
        return obj

    @property
    def name(self):
        return self._value_

    @classmethod
    def from_string(cls, name):
        try:
            return cls[name]
        except KeyError:
            raise ValueError(f"No type found with name '{name}'")

class Qualities(enum.Enum):
    UNIVERSAL = ("UNIVERSAL", "💫", 1.4, "A")
    SUPREME = ("SUPREME", "✨", 1.3, "B")
    GREAT = ("GREAT", "⏫", 1.2, "C")
    GOOD = ("GOOD", "🔼", 1, "D")
    SUB_PAR = ("SUB_PAR", "🔽", 0.95, "E")
    BAD = ("BAD", "⏬", 0.9, "F")

    def __new__(cls, name, emoji, coef, rank):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.emoji = emoji
        obj.coef = coef
        obj.rank = rank
        return obj

    @property
    def name(self):
        return self._value_

    @classmethod
    def from_string(cls, name):
        try:
            return cls[name]
        except KeyError:
            raise ValueError(f"No quality found with name '{name}'")

def get_type_from_string(typ:str):
    if typ == "ATTACK":
        return Types.ATTACK
    elif typ == "DEFENSE":
        return Types.DEFENSE
    elif typ == "SPEED":
        return Types.SPEED
    elif typ == "LUCK":
        return Types.LUCK
    elif typ == "BALANCE":
        return Types.BALANCE
    else:
        raise ValueError(f"No quality found with name '{typ}'")

def get_qualities_from_string(quality:str):
    if quality == "UNIVERSAL":
        return Qualities.UNIVERSAL
    elif quality == "SUPREME":
        return Qualities.SUPREME
    elif quality == "GREAT":
        return Qualities.GREAT
    elif quality == "GOOD":
        return Qualities.GOOD
    elif quality == "SUB_PAR":
        return Qualities.SUB_PAR
    elif quality == "BAD":
        return Qualities.BAD
    else:
        raise ValueError(f"No quality found with name '{quality}'")