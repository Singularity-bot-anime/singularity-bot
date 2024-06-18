import random
from typing import TYPE_CHECKING, List
from singularitybot.models.gameobjects.effects import Effect, EffectType

if TYPE_CHECKING:
    from singularitybot.models.gameobjects.character import Character

def get_payload():
    return {}

def choji_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_hp *= 2
    character.current_speed += 50
    health_boost_effect = Effect(EffectType.HEALTHBOOST, duration=3, value=character.current_hp)
    character.effects.append(health_boost_effect)
    message = f"{character.name} gains double HP and 50 more speed."
    return payload, message

def ebisu_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    lowest_health_ally = min(allied_characters, key=lambda ally: ally.current_hp)
    heal_amount = int(0.05 * lowest_health_ally.base_hp)
    lowest_health_ally.current_hp += heal_amount
    regeneration_effect = Effect(EffectType.REGENERATION, duration=3, value=heal_amount)
    lowest_health_ally.effects.append(regeneration_effect)
    message = f"{character.name} heals {lowest_health_ally.name} for 5% of their base HP."
    return payload, message

def hinata_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    damage_up_effect = Effect(EffectType.DAMAGEUP, duration=3, value=character.base_damage)
    character.effects.append(damage_up_effect)
    message = f"{character.name} empowers her next 3 attacks."
    return payload, message

def ino_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    target = random.choice(enemy_characters) if len(enemy_characters) > 1 else enemy
    enemy.attack(target)
    message = f"{character.name} makes {enemy.name} attack {target.name}."
    return payload, message

def konohamaru_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    extra_damage = character.base_damage * 2
    enemy.current_hp -= extra_damage
    burn_effect = Effect(EffectType.BURN, duration=2, value=extra_damage)
    enemy.effects.append(burn_effect)
    message = f"{character.name} uses Rasengan to deal {extra_damage} extra damage to {enemy.name}."
    return payload, message

def kurenai_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    slow_effect = Effect(EffectType.SLOW, value=25, duration=3)
    enemy.effects.append(slow_effect)
    message = f"{character.name} slows {enemy.name} by 25%."
    return payload, message

def sakura_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    message = f"{character.name} stands there."
    return payload, message

def shikamaru_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemies = random.sample(enemy_characters, 2)
    for enemy in enemies:
        stun_effect = Effect(EffectType.STUN, duration=1, value=0)
        enemy.effects.append(stun_effect)
    message = f"{character.name} stuns two enemies."
    return payload, message

def neji_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    weaken_effect = Effect(EffectType.WEAKEN, duration=3, value=20)
    character.effects.append(weaken_effect)
    message = f"{character.name} counters attacks, reducing incoming damage by 20%."
    return payload, message

def tenten_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        bleed_effect = Effect(EffectType.BLEED, duration=3, value=10)
        enemy.effects.append(bleed_effect)
    message = f"{character.name} deals 30 damage to all enemies."
    return payload, message

def rocklee_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    damage_up_effect = Effect(EffectType.DAMAGEUP, duration=3, value=25)
    character.effects.append(damage_up_effect)
    message = f"{character.name} gains 25 more damage."
    return payload, message

def kiba_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        speed_up_effect = Effect(EffectType.SLOW, duration=3, value=-50)
        ally.effects.append(speed_up_effect)
    message = f"{character.name} increases all allies' speed by 50."
    return payload, message

def asuma_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    speed_up_effect = Effect(EffectType.SLOW, duration=3, value=-25)
    damage_up_effect = Effect(EffectType.DAMAGEUP, duration=3, value=25)
    character.effects.append(speed_up_effect)
    character.effects.append(damage_up_effect)
    message = f"{character.name} gains 25 more speed and 25 more damage."
    return payload, message

def kurenai_aoe_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        confuse_effect = Effect(EffectType.WEAKEN, duration=2, value=0)
        enemy.effects.append(confuse_effect)
    message = f"{character.name} confuses all enemies."
    return payload, message

def sasuke_sr_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    health_boost_effect = Effect(EffectType.HEALTHBOOST, duration=3, value=character.current_hp)
    enemy.current_hp = character.current_hp
    enemy.effects.append(health_boost_effect)
    message = f"{character.name} drops {enemy.name}'s health to his own."
    return payload, message

def itachi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    stun_effect = Effect(EffectType.STUN, duration=2, value=0)
    enemy.effects.append(stun_effect)
    message = f"{character.name} stuns {enemy.name} for 2 rounds."
    return payload, message

def kakashi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    ur_specials = [naruto_special, jiraiya_special]  # Assuming these are UR specials
    special = random.choice(ur_specials)
    special_payload, special_message = special(character, allied_characters, enemy_characters)
    message = f"{character.name} copies a UR special: {special_message}"
    return payload, message

def sasuke_ssr_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        armor_effect = Effect(EffectType.WEAKEN, duration=3, value=10)
        enemy.armor *= 0.9
        enemy.effects.append(armor_effect)
    message = f"{character.name} ignores 10% of all enemies' armor."
    return payload, message

def zabuza_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        if EffectType.BLEED in [effect.type for effect in enemy.effects]:
            extra_damage = Effect(EffectType.BURN, duration=2, value=character.base_damage)
            enemy.current_hp -= character.base_damage
            enemy.effects.append(extra_damage)
    message = f"{character.name} deals extra damage to bleeding enemies."
    return payload, message

def jiraiya_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    damage_reduction_effect = Effect(EffectType.WEAKEN, duration=3, value=20)
    character.effects.append(damage_reduction_effect)
    message = f"{character.name} reduces incoming damage by 20%."
    return payload, message

def naruto_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_hp *= 2
    character.current_damage *= 2
    for ally in allied_characters:
        fire_damage = int(0.1 * ally.base_hp)
        burn_effect = Effect(EffectType.BURN, duration=3, value=fire_damage)
        ally.current_hp -= fire_damage
        ally.effects.append(burn_effect)
    message = f"{character.name} doubles his damage and HP for 3 turns but inflicts fire damage to allies."
    return payload, message

def not_implemented(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    message = f"｢{character.name}｣ has no power yet"
    payload["is_a_special"] = False
    return payload, message

specials = {
    "1": choji_special,
    "2": ebisu_special,
    "3": hinata_special,
    "4": ino_special,
    "5": konohamaru_special,
    "6": kurenai_special,
    "7": sakura_special,
    "8": tenten_special,
    "9": not_implemented,
    "10": not_implemented,
    "11": rocklee_special,
    "12": kiba_special,
    "13": asuma_special,
    "14": kurenai_aoe_special,
    "15": rocklee_special,
    "16": shikamaru_special,
    "17": None,
    "18": None,
    "19": None,
    "20": itachi_special,
    "21": kakashi_special,
    "22": sasuke_ssr_special,
    "23": zabuza_special,
    "24": jiraiya_special,
    "25": naruto_special,
}
