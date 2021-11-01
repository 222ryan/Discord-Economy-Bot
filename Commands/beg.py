import random
import re

import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Beg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def beg(self, ctx):
        server = economy.find({"guildid": ctx.guild.id, "id": {"$exists": True}})
        stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
        money = stats['money']
        amount = random.randint(10, 30)
        users = []
        for doc in server:
            users.append(doc['id'])
        if ctx.author.id in users:
            users.remove(ctx.author.id)
        user = random.choice(users)

        begs = [f"{self.client.user.mention} donated you `{currency}{amount}` [POSITIVE]", f"A nearby pedestrian handed you `{currency}{amount}` [POSITIVE]", f"You begged the wrong person and got robbed of `{currency}{amount}` [NEGATIVE]", f"You begged <@{user}> for money, however they ended up robbing you of `{currency}{amount}` [ROB]"]

        begs_picker = random.choice(begs)
        positive_check = re.search("POSITIVE", begs_picker)
        negative_check = re.search("NEGATIVE", begs_picker)
        if positive_check:
            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                               {"$set": {"money": money + int(amount)}})

            embed = discord.Embed(description=str(begs_picker).replace("[POSITIVE]", ''))
            await ctx.send(embed=embed)
            return
        if negative_check:
            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                               {"$set": {"money": money - int(amount)}})
            embed = discord.Embed(description=str(begs_picker).replace("[NEGATIVE]", ''))
            await ctx.send(embed=embed)
            return
        if not positive_check or not negative_check:
            userstats = economy.find_one({"guildid": ctx.guild.id, "id": user})
            user_money = userstats['money']
            economy.update_one({"guildid": ctx.guild.id, "id": user},
                               {"$set": {"money": user_money + int(amount)}})
            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                               {"$set": {"money": money - int(amount)}})
            embed = discord.Embed(description=str(begs_picker).replace("[ROB]", ''))
            await ctx.send(embed=embed)
            return


def setup(client):
    client.add_cog(Beg(client))