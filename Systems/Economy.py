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
        if config['private_message'] is True:
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
                                       {"$set": {"money": int(config['starting_money']), "job": "None", "daily_income": 0, "name": f"{member.name}", "inventory": [], "inventory_amount": [], 'small_vault': 0, 'medium_vault': 0, 'large_vault': 0}})
                    print(f"[Modern Economy] User: {member} already found in database, Updating Fields.")
                else:
                    newuser = {"guildid": member.guild.id, "id": member.id,
                               "money": int(config['starting_money']),
                               "job": "None", "daily_income": 0, "name": f"{member.name}", "inventory": [], "inventory_amount": [], 'small_vault': 0, 'medium_vault': 0, 'large_vault': 0}
                    economy.insert_one(newuser)
                    print(f"[Modern Economy] User: {member} has been added to the Database!")


    @commands.command()
    async def databaseregister(self, ctx):
        if ctx.author.id == config['bot_owner_id']:
            embed = discord.Embed(title="❓ // ARE YOU SURE?", description="This will do the following: \n\n➤ Reset Every Users Money ✅\n➤ Quit Every Users Jobs ✅\n➤ Reset The Leaderbaord ✅\n➤ Reset any stats to do with Modern Levels ❌")
            message = await ctx.send(embed=embed)

            # allow the user to react to the message
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            # check if yes or no is reacted to
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

            # wait for a reaction
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

                # if the user reacted with yes
                if str(reaction.emoji) == "✅":
                    await ctx.send("Registering all users in the database... This may take some time.")
                    for guild in self.client.guilds:
                        for member in guild.members:
                            if not member.bot:
                                user = economy.find_one({"guildid": guild.id, "id": member.id})
                                if user:
                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                       {"$set": {"money": int(config['starting_money']), "job": "None",
                                                                 "daily_income": 0, "name": f"{member}", "inventory": [],
                                                                 "inventory_amount": [], 'small_vault': 0, 'medium_vault': 0,
                                                                 'large_vault': 0}})
                                    print(f"[Modern Economy] User: {member} already found in database, Updating Fields.")
                                    jobs = economy.find_one({"guildid": guild.id, "id": member.id, "job_type": {"$exists": True}})
                                    if jobs:
                                        economy.delete_one(jobs)
                                else:
                                    newuser = {"guildid": guild.id, "id": member.id,
                                               "money": int(config['starting_money']),
                                               "job": "None", "daily_income": 0, "name": f"{member}", "inventory": [],
                                               "inventory_amount": [], 'small_vault': 0, 'medium_vault': 0, 'large_vault': 0}
                                    economy.insert_one(newuser)
                                    print(f"[Modern Economy] User: {member} has been added to the Database!")

                    embed = discord.Embed(title=f"✅ // Database Register Complete")

                    await message.edit(embed=embed)

                    # remove reactions
                    await message.clear_reactions()

                # if the user reacted with no
                elif str(reaction.emoji) == "❌":
                    embed = discord.Embed(title=f"❌ // Database Register Cancelled")
                    await message.edit(embed=embed)
                    await message.clear_reactions()

            # if the user didn't react with yes or no
            except asyncio.TimeoutError:
                embed = discord.Embed(title=f"❌ // Database Register Timed Out")
                await message.edit(embed=embed)
                await message.clear_reactions()









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
                                   {"$set": {"money": int(config['starting_money']), "job": "None", "daily_income": 0, "name": f"{member.name}", "inventory": [], "inventory_amount": [], 'small_vault': 0, 'medium_vault': 0, 'large_vault': 0}})
                print(f"[Modern Economy] User: {member} already found in database, Updating Fields.")
            else:
                newuser = {"guildid": member.guild.id, "id": member.id,
                           "money": int(config['starting_money']),
                           "job": "None", "daily_income": 0, "inventory": [], "inventory_amount": [], 'small_vault': 0, 'medium_vault': 0, 'large_vault': 0}
                economy.insert_one(newuser)
                print(f"[Modern Economy] User: {member} has been added to the Database!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            economy.delete_one({"server": member.guild.id, "id": member.id})
            print(f"[Modern Economy] User: {member.id} has been removed from the database!")


def setup(client):
    client.add_cog(Economy(client))
