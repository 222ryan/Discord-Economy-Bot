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


class rob(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Pay Command
    @commands.cooldown(1, 60 * 30, commands.BucketType.user)
    @commands.command()
    async def rob(self, ctx, member: discord.Member = None):
        if member is None:
            embed = discord.Embed(description=":x: You need to specify who you would like to rob!")
            await ctx.send(embed=embed)
        if member == ctx.author:
            embed = discord.Embed(description=":x: You cannot rob yourself!")
            await ctx.send(embed=embed)
            return
        if not member.bot:
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
            userstats = economy.find_one({"guildid": ctx.guild.id, "id": user})
            user_money = userstats['money']
            if int(user_money) < amount:
                embed = discord.Embed(description=f":x: {member.mention} has insufficient money to be robbed!")
                await ctx.send(embed=embed)
                return
            begs = [f"You robbed {member.mention} out of {currency}{amount}! [POSITIVE]", f"You tried robbing {member.mention}, but they ended up robbing you out of {currency}{amount} [ROB]", f"You failed to rob {member.mention} [NEGATIVE]"]

            begs_picker = random.choice(begs)
            positive_check = re.search("POSITIVE", begs_picker)
            negative_check = re.search("NEGATIVE", begs_picker)
            if positive_check:
                userstats = economy.find_one({"guildid": ctx.guild.id, "id": user})
                user_money = userstats['money']
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": money + int(amount)}})
                economy.update_one({"guildid": ctx.guild.id, "id": int(user)},
                                   {"$set": {"money": user_money - int(amount)}})
                embed = discord.Embed(description=str(begs_picker).replace("[POSITIVE]", ''))
                await ctx.send(embed=embed)
                return
            if negative_check:
                embed = discord.Embed(description=str(begs_picker).replace("[NEGATIVE]", ''))
                await ctx.send(embed=embed)
                return
            if not positive_check or not negative_check:
                userstats = economy.find_one({"guildid": ctx.guild.id, "id": user})
                user_money = userstats['money']
                economy.update_one({"guildid": ctx.guild.id, "id": member.id},
                                   {"$set": {"money": user_money + int(amount)}})
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": money - int(amount)}})
                embed = discord.Embed(description=str(begs_picker).replace("[ROB]", ''))
                await ctx.send(embed=embed)
                return
        else:
            embed = discord.Embed(description=":x: You cannot rob bots!")
            await ctx.send(embed=embed)
            return






def setup(client):
    client.add_cog(rob(client))