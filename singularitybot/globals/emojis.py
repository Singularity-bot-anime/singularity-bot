import disnake

from enum import Enum


class CustomEmoji(str, Enum):
    ONE: disnake.PartialEmoji = "<:emote1:1097083211571544126>"
    TWO: disnake.PartialEmoji = "<:emote2:1097083214142640218>"
    THREE: disnake.PartialEmoji = "<:emote3:1097083215744872458>"
    FOUR: disnake.PartialEmoji = "<:emote4:1097083218282418246>"
    FIVE: disnake.PartialEmoji = "<:emote5:1097083219632992328>"
    SIX: disnake.PartialEmoji = "<:emote6:1097083221973413918>"
    SEVEN: disnake.PartialEmoji = "<:emote7:1097083222992617493>"
    EIGHT: disnake.PartialEmoji = "<:emote8:1097083224485797928>"
    NINE: disnake.PartialEmoji = "<:emote9:1097083226436161537>"
    TEN: disnake.PartialEmoji = "<:emote10:1097083227656704000>"

    R_R:disnake.PartialEmoji = "<:emoteR:1097084723437772810>"
    R_SR:disnake.PartialEmoji = "<:emoteSR:1097084724750585937>"
    R_SSR:disnake.PartialEmoji = "<:emoteSSR:1097084726004695110>"
    R_UR:disnake.PartialEmoji = "<:emoteUR:1097084728357703760>"
    R_LR:disnake.PartialEmoji = "<:emoteLR:1097084721290301511>"
    
    FRAGMENTS: disnake.PartialEmoji = "<:fragments:1097071904629727292>"
    SUPER_FRAGMENTS: disnake.PartialEmoji = "<:superfragments:1097071910409482260>"

    HEALING:disnake.PartialEmoji = "<:heal:1096245938588233818>"
    STUNNED: disnake.PartialEmoji = "<:stunned:1097076099072151692>"
    POISON: disnake.PartialEmoji = "<:poison:1096245940656021554>"
    WEAK: disnake.PartialEmoji = "<:weakened:1096245942736400435>"
    SLOW: disnake.PartialEmoji = "<:slowed:1096245941788483614>"
    DAMAGEUP :disnake.PartialEmoji = "<:damageboost:1097094159451557999>"
    LOADING_ICON: disnake.PartialEmoji = "<a:load:1097085411777589361>"

    def __str__(self):
        return str(self.value)
 

converter = {
    "R":CustomEmoji.R_R,
    "SR":CustomEmoji.R_SR,
    "SSR":CustomEmoji.R_SSR,
    "UR":CustomEmoji.R_UR,
    "LR":CustomEmoji.R_LR,
}
converter_exclame = {
    "R":"",
    "SR":"",
    "SSR":"❗",
    "UR":"‼️",
    "LR":"⁉️",
}