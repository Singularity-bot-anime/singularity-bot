import random
from typing import TYPE_CHECKING, List
from singularitybot.models.gameobjects.effects import Effect, EffectType

if TYPE_CHECKING:
    from singularitybot.models.gameobjects.character import Character

specials = {}

def get_payload():
    return {"is_a_special": True,"king_crimson":False}

def choji_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_hp *= 2
    character.current_speed += 5
    health_boost_effect = Effect(EffectType.HEALTHBOOST, duration=3, value=character.current_hp,sender=character)
    character.effects.append(health_boost_effect)
    message = f"{character.name} gains double HP and 50 more speed."
    return payload, message

specials["1"] = choji_special

def ebisu_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    lowest_health_ally = min(allied_characters, key=lambda ally: ally.current_hp)
    heal_amount = int(0.05 * lowest_health_ally.base_hp + character.current_critical)
    regeneration_effect = Effect(EffectType.REGENERATION, duration=3, value=heal_amount/3,sender=character)
    lowest_health_ally.effects.append(regeneration_effect)
    message = f"{character.name} heals {lowest_health_ally.name} for {heal_amount} in 3 turn"
    return payload, message

specials["2"] = ebisu_special

def hinata_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    damage_up_effect = Effect(EffectType.DAMAGEUP, duration=3, value=character.base_damage//4,sender=character)
    character.effects.append(damage_up_effect)
    message = f"{character.name} empowers her next 3 attacks."
    return payload, message

specials["3"] = hinata_special

def ino_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    target = random.choice(enemy_characters) if len(enemy_characters) > 1 else enemy
    enemy.attack(target)
    message = f"{character.name} makes {enemy.name} attack {target.name}."
    return payload, message

specials["4"] = ino_special

def konohamaru_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    extra_damage = character.base_damage * 0.25
    character.attack(enemy,multiplier=0.25)
    message = f"{character.name} uses Rasengan to deal {extra_damage} extra damage to {enemy.name}."
    return payload, message

specials["5"] = konohamaru_special

def kurenai_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    slow_effect = Effect(EffectType.SLOW, value=25, duration=3,sender=character)
    enemy.effects.append(slow_effect)
    message = f"{character.name} slows {enemy.name} by 25%."
    return payload, message

specials["6"] = kurenai_special

def sakura_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    message = f"{character.name} stands there."
    return payload, message

specials["7"] = sakura_special

def tenten_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        bleed_effect = Effect(EffectType.BLEED, duration=3, value=10)
        enemy.effects.append(bleed_effect)
    message = f"{character.name} deals 30 damage to all enemies."
    return payload, message

specials["8"] =tenten_special

def teuchi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        heal_amount = int(0.1 * ally.base_hp)
        ally.current_hp += heal_amount
    message = f"{character.name} heals everyone for 10% of their base HP."
    return payload, message

specials["9"] = teuchi_special

def tsubaki_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    slow_effect = Effect(EffectType.SLOW, value=10, duration=2)
    enemy.effects.append(slow_effect)
    message = f"{character.name} slows {enemy.name} by 10%."
    return payload, message

specials["10"] = tsubaki_special

def might_guy_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        if ally != character:
            attack_boost_effect = Effect(EffectType.DAMAGEUP, duration=3, value=5)
            ally.effects.append(attack_boost_effect)
    message = f"{character.name} gives words of advice, boosting allies' attack damage by 5."
    return payload, message

specials["11"] = might_guy_special


def haku_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        bleed_effect = Effect(EffectType.BLEED, duration=3, value=15,sender=character)
        slow_effect = Effect(EffectType.SLOW, duration=3, value=10,sender=character)
        enemy.effects.append(bleed_effect)
        enemy.effects.append(slow_effect)
    message = f"{character.name} uses Needle Drop, causing bleeding and slowing down enemies."
    return payload, message

specials["12"] = haku_special

def kiba_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        dmg_up= Effect(EffectType.DAMAGEUP,1,character.base_damage,sender=character)
        character.effects.append(dmg_up)
    message = f"{character.name} increases all allies' speed by 50."
    return payload, message

specials["13"] = kiba_special

def neji_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    weaken_effect = Effect(EffectType.WEAKEN, duration=3, value=0.9)
    character.effects.append(weaken_effect)
    message = f"{character.name} counters attacks, reducing incoming damage by 20%."
    return payload, message

specials["14"] = neji_special

def rocklee_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    damage_up_effect = Effect(EffectType.DAMAGEUP, duration=2, value=25)
    character.effects.append(damage_up_effect)
    message = f"{character.name} gains 25 more damage."
    return payload, message

specials["15"] = rocklee_special

def shikamaru_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    slowest_enemy = min(enemy_characters, key=lambda enemy: enemy.current_speed)
    stun_effect = Effect(EffectType.STUN, duration=1, value=0)
    slowest_enemy.effects.append(stun_effect)
    message = f"{character.name} stuns the slowest enemy, {slowest_enemy.name}, for 1 turn."
    return payload, message

specials["16"] = shikamaru_special

def shino_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemies = random.sample(enemy_characters, 2)
    for enemy in enemies:
        poison = Effect(EffectType.POISON, duration=3, value=10,sender=character)
        enemy.effects.append(poison)
    message = f"{character.name} poison every ennemies. for 10 damage"
    return payload, message

specials["17"] = shino_special

def tsunade_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    random_ally = random.choice(allied_characters)
    heal_amount = int(0.10 * random_ally.base_hp)
    random_ally.current_hp += heal_amount
    regeneration_effect = Effect(EffectType.REGENERATION, duration=3, value=heal_amount)
    random_ally.effects.append(regeneration_effect)
    message = f"{character.name} heals {random_ally.name} for 30% of their base HP."
    return payload, message

specials["18"] = tsunade_special


def hiruzen_sarutobi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    if enemy.current_hp > character.current_hp:
        enemy.current_hp /= 2
    else:    
        enemy.current_hp = character.current_hp
    message = f"{character.name} drops {enemy.name}'s health to his own."
    return payload, message

specials["19"] = hiruzen_sarutobi_special

def itachi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    stun_effect = Effect(EffectType.STUN, duration=2, value=0)
    enemy.effects.append(stun_effect)
    message = f"{character.name} stuns {enemy.name} for 2 rounds."
    return payload, message

specials["20"] = itachi_special

def kakashi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    ur_specials = [goku_ssj1_special,naruto_special, jiraiya_special,freezer_full_power_special]  # Assuming these are UR specials
    special = random.choice(ur_specials)
    special_payload, special_message = special(character, allied_characters, enemy_characters)
    message = f"{character.name} copies a UR special: {special_message}"
    return payload, message

specials["21"] = kakashi_special

def sasuke_ssr_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        armor_effect = Effect(EffectType.WEAKEN, duration=3, value=0.7)
        enemy.effects.append(armor_effect)
    message = f"{character.name} ignores 50% of all enemies' armor."
    return payload, message

specials["22"] = sasuke_ssr_special

def zabuza_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        if EffectType.BLEED in [effect.type for effect in enemy.effects]:
            enemy.current_hp -= character.base_damage
    message = f"{character.name} deals extra damage to bleeding enemies."
    return payload, message

specials["23"] = zabuza_special

def jiraiya_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.armor += 100
    character.current_damage += 50
    message = f"{character.name} reduces incoming damage by 20%."
    return payload, message

specials["24"] = jiraiya_special

def naruto_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_hp = 2*character.start_hp
    character.current_damage = 2*character.start_damage
    for ally in allied_characters:
        fire_damage = int(0.1 * ally.base_hp)
        burn_effect = Effect(EffectType.BURN, duration=3, value=fire_damage)
        ally.effects.append(burn_effect)
    message = f"{character.name} doubles his damage and HP but inflicts fire damage to allies."
    return payload, message

specials["25"] = naruto_special

def freezer_full_power_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_damage = 2*character.start_damage
    message = f"{character.name} unleashes full power, doubling damage for 5 turns."
    return payload, message

specials["26"] = freezer_full_power_special

def freezer_final_form_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        aoe_damage = character.base_damage * 0.5
        enemy.current_hp -= aoe_damage
    message = f"{character.name} uses Final Form, dealing massive AoE {aoe_damage} to all enemies."
    return payload, message

specials["27"] = freezer_final_form_special

def goku_ssj1_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_damage *= 1.5
    character.current_speed *= 1.2
    message = f"{character.name} uses Saiyan Rage, increasing damage by 50% and speed by 20%."
    return payload, message

specials["28"] = goku_ssj1_special 

def goku_ssj1_transforming_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_damage *= 2
    character.current_speed *= 2
    message = f"{character.name} transforms, boosting stats over 3 turns."
    return payload, message

specials["29"] = goku_ssj1_transforming_special

def freezer_second_form_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    death_beam_damage = character.base_damage * 0.5
    enemy.current_hp -= death_beam_damage
    message = f"{character.name} unleashes Death Beam, dealing {death_beam_damage} damage to {enemy.name}."
    return payload, message

specials["30"] = freezer_second_form_special

def goku_kaioken_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_damage *= 1.1
    character.current_speed *= 1.1
    message = f"{character.name} uses Kaioken Attack, boosting damage and speed."
    return payload, message

specials["31"] = goku_kaioken_special

def piccolo_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    regeneration_effect = Effect(EffectType.REGENERATION, duration=2, value=int(character.base_hp * 0.1))
    character.effects.append(regeneration_effect)
    message = f"{character.name} uses Regeneration, healing 20% of max HP "
    return payload, message

specials["32"] = piccolo_special

def vegeta_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_critical += 20
    character.current_damage *= 1.5
    message = f"{character.name} uses Pride of Saiyan, increasing critical rate and damage."
    return payload, message

specials["33"] = vegeta_special


def carrot_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_speed += 2
    character.current_damage += 2
    message = f"{character.name} uses Swift Attack, increasing speed and damage."
    return payload, message

specials["34"] = carrot_special

def brulee_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        reflect_damage = enemy.current_damage * 0.1
        enemy.current_hp -= int(reflect_damage)
    message = f"{character.name} uses Mirror World, reflecting 30% of the damage back to enemies."
    return payload, message

specials["35"] = brulee_special

def foxy_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        slow_effect = Effect(EffectType.SLOW, duration=3, value=5)
        enemy.effects.append(slow_effect)
    message = f"{character.name} uses Slow Beam, decreasing enemies' speed."
    return payload, message

specials["36"] = foxy_special

def inuarashi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        if ally != character:
            attack_boost_effect = Effect(EffectType.DAMAGEUP, duration=3, value=20)
            ally.effects.append(attack_boost_effect)
    message = f"{character.name} uses Duke's Fury, increasing allies' damage."
    return payload, message

specials["37"] = inuarashi_special

def momonosuke_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_hp += 100
    character.current_damage += 40
    message = f"{character.name} uses Dragon Form, increasing HP and damage."
    return payload, message

specials["38"] = momonosuke_special

def nekomamushi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_critical += 20
    message = f"{character.name} uses Cat Viper's Wrath, increasing critical rate."
    return payload, message

specials["39"] = nekomamushi_special

def senor_pink_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        damage_reduction_effect = Effect(EffectType.WEAKEN, duration=3, value=0.9)
        enemy.effects.append(damage_reduction_effect)
    message = f"{character.name} uses Baby Shower, reducing enemies' damage."
    return payload, message

specials["40"] = senor_pink_special

def speed_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    character.current_speed += 5
    message = f"{character.name} uses Blazing Speed, increasing speed and evasion."
    return payload, message

specials["41"] = speed_special

def vivi_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        ally.armor += 50
    message = f"{character.name} uses Princess' Command, buffing allies' defense."
    return payload, message

specials["42"] = vivi_special

def arlong_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    high_damage = character.base_damage * 0.5
    enemy.current_hp -= high_damage
    message = f"{character.name} uses Shark On Darts, dealing high damage to {enemy.name}."
    return payload, message

specials["43"] = arlong_special

def bartolomeo_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    barrier_effect = Effect(EffectType.HEALTHBOOST, duration=2, value=int(character.base_hp * 0.5))
    character.effects.append(barrier_effect)
    message = f"{character.name} uses Barrier powers, absorbing damage for 2 turns."
    return payload, message

specials["44"] = bartolomeo_special

def moria_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        shadow_damage = character.base_damage * 1.2
        enemy.current_hp -= shadow_damage
    message = f"{character.name} uses Shadow Revolution, summoning shadows to attack enemies."
    return payload, message

specials["45"] = moria_special

def jewelry_bonney_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    armor_reduction_effect = Effect(EffectType.WEAKEN, duration=3, value=0.9)
    enemy.effects.append(armor_reduction_effect)
    message = f"{character.name} uses Age Manipulation, altering {enemy.name}'s stats."
    return payload, message

specials["46"] = jewelry_bonney_special

def koby_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        attack_boost_effect = Effect(EffectType.DAMAGEUP, duration=3, value=int(character.base_damage * 0.3))
        ally.effects.append(attack_boost_effect)
    message = f"{character.name} uses Determination, boosting allies' attack for 3 turns."
    return payload, message

specials["47"] = koby_special


def usopp_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    critical_damage = character.base_damage * 2
    enemy.current_hp -= critical_damage
    message = f"{character.name} uses Sniper Shot, dealing high critical damage to {enemy.name}."
    return payload, message

specials["48"] = usopp_special

def doflamingo_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        control_effect = Effect(EffectType.STUN, duration=1, value=0)
        enemy.effects.append(control_effect)
    message = f"{character.name} uses Puppet Master, controlling enemies for 2 turns."
    return payload, message

specials["49"] = doflamingo_special

def issho_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        gravity_effect = Effect(EffectType.STUN, duration=2, value=0)
        enemy.effects.append(gravity_effect)
    message = f"{character.name} uses Gravity Manipulation, immobilizing enemies for 2 turns."
    return payload, message

specials["50"] = issho_special
def jinbei_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    enemy = random.choice(enemy_characters)
    extra_damage = character.base_damage * 2
    enemy.current_hp -= extra_damage
    message = f"{character.name} uses Fish-Man Karate, dealing extra damage to {enemy.name}."
    return payload, message

specials["51"] = jinbei_special

def katakuri_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for enemy in enemy_characters:
        aoe_damage = character.base_damage * 1.5
        enemy.current_hp -= aoe_damage
    message = f"{character.name} uses Mochi Mastery, dealing high AoE damage."
    return payload, message

specials["52"] = katakuri_special

def uta_special(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    for ally in allied_characters:
        buff_effect = Effect(EffectType.DAMAGEUP, duration=3, value=int(character.base_damage * 0.3))
        ally.effects.append(buff_effect)
    message = f"{character.name} uses Melodic Charm, buffing allies' stats for 3 turns."
    return payload, message

specials["53"] = uta_special


def the_world(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    multiplier = 0.6
    damage = 0
    for ennemy in ennemy_stand:
        damage += stand.attack(ennemy, multiplier=multiplier)["damage"]
    message = f"｢{stand.name}｣ STOPS TIME! and damages everyone for {int(damage)}"
    return payload, message


def star_platinum_the_world(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    multiplier = 0.6
    damage = 0
    for ennemy in ennemy_stand:
        damage += stand.attack(ennemy, multiplier=multiplier)["damage"]
    message = f"｢{stand.name}｣ STOPS TIME! and damages everyone for {int(damage)}"
    return payload, message

def crazy_diamond(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    valid_stand = [i for i in allied_stand if i.is_alive() and i != stand]
    if len(valid_stand) != 0:
        ally: "Stand" = random.choice(valid_stand)
        dif_damage = abs(stand.start_hp - stand.current_hp)
        heal = min(ally.start_hp, ally.current_hp + (dif_damage // 2))
        ally.current_hp = heal
        message = f"｢{stand.name}｣ heals {ally.name}"
    else:
        message = f"｢{stand.name}｣ enraged!"
    return payload, message



def killer_queen_bite_the_dust(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    heal = (stand.start_hp - stand.current_hp) // 3
    stand.current_hp += heal
    stand.current_hp = max(0, min(stand.current_hp, stand.start_hp))
    message = f"｢{stand.name}｣ resets the timeline! and heals for {heal}"
    return payload, message


def gold_experience(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    multiplier = 30
    payload = get_payload()
    for allies in allied_stand:
        if allies.current_hp < allies.start_hp:
            allies.current_hp += 30
            allies.current_hp = min(allies.start_hp, allies.current_hp)
    message = f"｢{stand.name}｣ heals it's ally for {multiplier}"
    return payload, message

def king_crimson(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    payload["king_crimson"] = True
    message = f"｢{stand.name}｣ has already..."
    return payload, message


def gold_experience_requiem(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    payload["GER"] = True
    valid_stand = [i for i in ennemy_stand if i.is_alive()]
    message = f"｢{stand.name}｣ You will never reach the truth, Return to Zero!"
    # reset their scaling
    for ennemy in ennemy_stand:
        ennemy: "Stand" = stand
        ennemy.current_hp = min(ennemy.current_hp, ennemy.start_hp)
        ennemy.current_damage = min(ennemy.current_damage, ennemy.start_damage)
        ennemy.current_speed = min(ennemy.current_speed, ennemy.start_speed)
    if len(valid_stand) != 0:
        target = random.choice(valid_stand)
        target.effects.append(Effect(EffectType.STUN, 2, 0, stand))
        message += f"｢{stand.name}｣ stunned {target.name}!"
    return payload, message


def stone_free(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    multiplier = 0.90
    payload = get_payload()
    valid_stand = [i for i in ennemy_stand if i.is_alive()]
    message = f"｢{stand.name}｣ frees the stone ocean!"
    if len(valid_stand) != 0:
        target = random.choice(valid_stand)
        target.effects.append(Effect(EffectType.STUN, 1, 0, stand))
        target.current_speed *= multiplier
    return payload, message

def made_in_heaven(
    stand: "Stand", allied_stand: List["Stand"], ennemy_stand: List["Stand"]
) -> tuple:
    payload = get_payload()
    stand.current_speed += 5
    stand.current_damage += 20
    stand.current_critical += 5
    message = f"｢{stand.name}｣'s speed increases!"
    return payload, message

def not_implemented(character: "Character", allied_characters: List["Character"], enemy_characters: List["Character"]) -> tuple:
    payload = get_payload()
    message = f"｢{character.name}｣ has no power yet"
    payload["is_a_special"] = False
    return payload, message
