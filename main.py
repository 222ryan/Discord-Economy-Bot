# Imports
from os import listdir

from discord.ext import commands

import discord
from discord.ext.commands import CommandInvokeError
from ruamel.yaml import YAML
import logging
import os
from dotenv import load_dotenv

from Systems.Economy import economy

load_dotenv()

# Opens the config and reads it, no need for changes unless you'd like to change the library (no need to do so unless having issues with ruamel)
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

leader_embed = config["leaderboard_embed_colour"]
embed_colour = config["embed_colour"]
error_embed_colour = config["error_embed_colour"]
success_embed_colour = config["success_embed_colour"]

# Command Prefix + Removes the default discord.py help command
client = commands.Bot(command_prefix=commands.when_mentioned_or(config['Prefix']), intents=discord.Intents.all(),
                      case_insensitive=True)
client.remove_command('help')

# sends discord logging files which could potentially be useful for catching errors.
FORMAT = '[%(asctime)s]:[%(levelname)s]: %(message)s'
logging.basicConfig(filename='Logs/logs.txt', level=logging.DEBUG, format=FORMAT)
logging.debug('Started Logging')
logging.info('Connecting to Discord.')

currency = config['currency_type']


@client.event  # On Bot Startup, Will send some details about the bot and sets it's activity and status. Feel free to remove the print messages, but keep everything else.
async def on_ready():
    config_status = config['bot_status_text']
    config_activity = config['bot_activity']
    activity = discord.Game(name=config['bot_status_text'])
    logging.info('Getting Bot Activity from Config')
    print("If you encounter any bugs, please let me know.")
    print('------')
    print('Logged In As:')
    print(f"Username: {client.user.name}\nID: {client.user.id}")
    print('------')
    print(f"Status: {config_status}\nActivity: {config_activity}")
    print('------')
    await client.change_presence(status=config_activity, activity=activity)
    # check if user has inventory and inventory amount in the database
    for member in client.get_all_members():
        if member.bot == False:
            users = economy.find({'guildid': member.guild.id, 'id': member.id, 'inventory': {'$exists': False},
                                  'inventory_amount': {'$exists': False}, "job_type": {'$exists': False}})
            for x in users:
                if x:
                    economy.update_one({'guildid': x['guildid'], 'id': x['id'], "inventory": {'$exists': False}},
                                       {'$set': {'inventory': [], 'inventory_amount': []}})
                    print(
                        f"[Modern Economy] User {member} was missing INVENTORY and INVENTORY_AMOUNT - Automatically added it!")
            name_check = economy.find({'guildid': member.guild.id, 'id': member.id, 'name': {'$exists': False}, "job_type": {'$exists': False}})
            for x in name_check:
                if x:
                    economy.update_one({'guildid': member.guild.id, 'id': x['id']}, {'$set': {'name': str(member)}})
                    print(f"[Modern Economy] User {member} was missing NAME - Automatically added it!")
            vault_check = economy.find({'guildid': member.guild.id, 'id': member.id, 'small_vault': {'$exists': False},
                                       "job_type": {'$exists': False}})
            for x in vault_check:
                if x:
                    economy.update_one({'guildid': member.guild.id, 'id': x['id']}, {'$set': {'small_vault': 0, 'medium_vault': 0, 'large_vault': 0}})
                    print(f"[Modern Economy] User {member} was missing VAULTS - Automatically added it!")


logging.info("------------- Loading -------------")
for fn in listdir("Commands"):
    if fn.endswith(".py"):
        logging.info(f"Loading: {fn}")
        client.load_extension(f"Commands.{fn[:-3]}")
        logging.info(f"Loaded {fn}")

logging.info(f"Loading: Economy System")
client.load_extension(f"Systems.Economy")
logging.info(f"Loaded Economy System")

logging.info("------------- Finished Loading -------------")

# Uses the bot token to login, so don't remove this.
token = os.getenv("DISCORD_TOKEN")
client.run(token)

# End Of Main
