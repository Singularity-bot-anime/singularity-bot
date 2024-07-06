import asyncio

# URL

WORMHOLEURL = "https://media1.tenor.com/m/xQ24GQOIYZAAAAAd/space.gif"
TOWERURL = "https://storage.stfurequiem.com/randomAsset/tower.png"
GANGURL = "https://media1.tenor.com/m/-fG6_QSIjZAAAAAC/amicreeper-galaxy.gif"

# Bot loop

LOOP = asyncio.get_event_loop()

# Stand Scaling

STXPTOLEVEL = 100
LEVEL_TO_STAT_INCREASE = 5
HPSCALING = 2
SPEEDSCALING = 10
DAMAGESCALING = 5
CRITICALSCALING = 50
CRITMULTIPLIER = 1.5
DODGENERF = 10
MAX_LEVEL = 100


# Fight Rewards

FRAGMENTSGAIN = 300
PLAYER_XPGAINS = 100
CHARACTER_XPGAINS = 10


# User scalings

USRXPTOLEVEL = 1000

# Crusade Items

CHANCEITEM = 10
DONOR_WH_WAIT_TIME = 1
NORMAL_WH_WAIT_TIME = 1.5

# Tower constants

ENTRYCOST = 500

# ADV

DONOR_ADV_WAIT_TIME = 6
NORMAL_ADV_WAIT_TIME = 6

# Shop

SHOPCREATIONCOST = 3000

ITEMTYPE = [
    "damage",
    "utility",
    "misc",
]
ITEMBYTYPE = {
    "damage": [{"id": 1}, {"id": 4}],
    "utility": [{"id": 2}, {"id": 3}],
}

# Gang

GANGCREATIONCOST = 10000

# Vote

SUPERFRAGMENT_VOTE = 1
COINS_VOTE = 250
