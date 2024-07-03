import json

# Load the characters data from the JSON file
with open('singularitybot/data/templates/characters.json', 'r') as file:
    data = json.load(file)

# Define the new attributes based on rarity
attributes_by_rarity = {
    "R": {"base_hp": 200, "base_damage": 50, "base_speed": 1, "base_critical": 5, "armor": 100},
    "SR": {"base_hp": 250, "base_damage": 50, "base_speed": 5, "base_critical": 5, "armor": 100},
    "SSR": {"base_hp": 300, "base_damage": 75, "base_speed": 10, "base_critical": 10, "armor": 100},
    "UR": {"base_hp": 350, "base_damage": 100, "base_speed": 15, "base_critical": 15, "armor": 100},
}

# Update the characters
for character in data['characters']:
    rarity = character['rarity']
    if rarity in attributes_by_rarity:
        character.update(attributes_by_rarity[rarity])

# Save the updated characters data to a new JSON file
with open('singularitybot/data/templates/updated_characters.json', 'w') as file:
    json.dump(data, file, indent=4)