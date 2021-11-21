import asyncio

import discord
from discord.ext import commands
from pymongo import MongoClient
from ruamel.yaml import YAML
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']
COLLECTION = os.getenv("COLLECTION")
DB_NAME = os.getenv("DATABASE_NAME")

# Please enter your mongodb details in the .env file.
cluster = MongoClient(MONGODB_URI)
economy = cluster[COLLECTION][DB_NAME]

# Reads the config file, no need for changing.
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if config['private_message'] is True:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            prefix = config['Prefix']
            embed = discord.Embed(title=f"👋 // Greetings, {guild.name}",
                                  description=f"Thanks for inviting me, my prefix here is: `{prefix}`")
            embed.add_field(name="🚀 | What's Next?",
                            value=f"`{prefix}help` displays every command you need to know for {self.client.user.mention}",
                            inline=False)
            embed.add_field(name="🧭 | Important Links:",
                            value=f"[Support Server](https://www.discord.gg/E56eZdNjK4) - Get support for {self.client.user.mention}")
            if guild.system_channel is None:
                await guild.create_text_channel('private', overwrites=overwrites)
                channel = discord.utils.get(guild.channels, name="private")
                if channel is None:
                    return
                await channel.send(embed=embed)
            else:
                await guild.system_channel.send(embed=embed)
        for member in guild.members:
            if not member.bot:
                user = economy.find_one({"guildid": guild.id, "id": member.id})
                if user:
                    economy.update_one({"guildid": guild.id, "id": member.id},
                                       {"$set": {"money": int(config['starting_money']), "job": "None", "daily_income": 0, "name": f"{member.name}", "inventory": [], "inventory_amount": []}})
                    print(f"[Modern Economy] User: {member} already found in database, Updating Fields.")
                else:
                    newuser = {"guildid": member.guild.id, "id": member.id,
                               "money": int(config['starting_money']),
                               "job": "None", "daily_income": 0, "name": f"{member.name}", "inventory": [], "inventory_amount": []}
                    economy.insert_one(newuser)
                    print(f"[Modern Economy] User: {member} has been added to the Database!")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        # Deletes all users when they bot is removed from the server
        for member in guild.members:
            if not member.bot:
                economy.delete_one({"guildid": guild.id, "id": member.id})
                print(f"[Modern Economy] Deleted {member} from the Database!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(3)
        if not member.bot:
            user = economy.find_one({"guildid": member.guild.id, "id": member.id})
            if user:
                economy.update_one({"guildid": member.guild.id, "id": member.id},
                                   {"$set": {"money": int(config['starting_money']), "job": "None", "daily_income": 0, "name": f"{member.name}", "inventory": [], "inventory_amount": []}})
                print(f"[Modern Economy] User: {member} already found in database, Updating Fields.")
            else:
                newuser = {"guildid": member.guild.id, "id": member.id,
                           "money": int(config['starting_money']),
                           "job": "None", "daily_income": 0, "inventory": [], "inventory_amount": []}
                economy.insert_one(newuser)
                print(f"[Modern Economy] User: {member} has been added to the Database!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            economy.delete_one({"server": member.guild.id, "id": member.id})
            print(f"[Modern Economy] User: {member.id} has been removed from the database!")


def setup(client):
    client.add_cog(Economy(client))
