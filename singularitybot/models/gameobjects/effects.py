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
}


class EffectType(Enum):
    STUN = "STUN"
    POISON = "POISON"
    WEAKEN = "WEAKEN"
    REGENERATION = "REGENERATION"
    SLOW = "SLOW"
    DAMAGEUP= "DAMAGEUP"


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
        self.emoji: disnake.PartialEmoji = Emoji[self.type.name]
        self.sender: Optional["Character"] = sender
