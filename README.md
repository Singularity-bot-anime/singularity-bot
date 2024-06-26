# Singularity bot

Singularity is an RPG discord bot with gacha features

## External Dependencies
- Redis database
- Python >= 9.0
- A discord TOKEN

## Installation

Use the package manager, [pip](https://pip.pypa.io/en/stable/) the dependencies.

```bash
python -m venv singularity
source /singularity/bin/activate
pip install -r requirements.txt  
```
You have to create a `.ENV` at the root of the project with a file containing the following parameters
```
DISCORD_KEY_SINGULARITY=<your discord token>
REDIS_URL=<your url uri>
```


## Usage

```
python singularitybot/bot.py
```

## Contributing

You can suggest change to this repository with pull request but, we recommend doing changes on your own fork

## License

[MIT](https://choosealicense.com/licenses/mit/)