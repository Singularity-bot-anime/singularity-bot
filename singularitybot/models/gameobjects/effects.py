import disnake

from enum import Enum

from typing import TYPE_CHECKING, Optional

# It's for typehint
if TYPE_CHECKING:
    from singularitybot.models.gameobjects.character import Character


Emoji = {
    "STUN": "<:stunned:1097076099072151692>",
    "POISON": "<:poison:1096245940656021554>",
    "WEAKEN": "<:weakened:1096245942736400435>",
    "REGENERATION": "<:slowed:1096245941788483614>",
    "DAMAGEUP":"<:damageboost:1097094159451557999>",
    "SLOW": "<:slowed:993988645520412702>",
    "BURN":"🔥",
    "BLEED":"🩸",
    "HEALTHBOOST":"💚"
}


class EffectType(Enum):
    STUN = "STUN"
    POISON = "POISON"
    WEAKEN = "WEAKEN"
    REGENERATION = "REGENERATION"
    SLOW = "SLOW"
    DAMAGEUP= "DAMAGEUP"
    BURN="BURN"
    BLEED="BLEED"
    HEALTHBOOST="HEALTHBOOST"


class Effect:
    def __init__(
        self,
        type: EffectType,
        duration: int,
        value: int,
        sender: Optional["Character"] = None,
    ):
        self.type: EffectType = type
        self.duration: int = duration
        self.value: int = value
        self.used: bool = False
        self.emoji: disnake.PartialEmoji = Emoji[self.type.name]
        self.sender: Optional["Character"] = sender

NEGATIVE_EFFECTS = [EffectType.POISON, EffectType.BURN, EffectType.BLEED,EffectType.STUN,EffectType.WEAKEN]
