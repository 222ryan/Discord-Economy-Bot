import random
import re

import discord
from discord.ext import commands
from ruamel.yaml import YAML

import kumoslab.functions
from Systems.Economy import economy
from main import currency, error_embed_colour, embed_colour

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
            embed = discord.Embed(description=":x: You need to specify who you would like to rob!", colour=error_embed_colour)
            await ctx.send(embed=embed)
        if member == ctx.author:
            embed = discord.Embed(description=":x: You cannot rob yourself!", colour=error_embed_colour)
            await ctx.send(embed=embed)
            return
        if not member.bot:
            server = economy.find({"guildid": ctx.guild.id, "id": {"$exists": True}})
            stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
            member_stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id})
            money = stats['money']
            money = await kumoslab.functions.getmoney(userid=member.id, guildid=ctx.guild.id)
            print(money)
            if int(money) <= 0:
                embed = discord.Embed(description=f":x: {member.mention} has no money to be robbed!",
                                      colour=error_embed_colour)
                await ctx.send(embed=embed)
                return

            amount = random.randint(1, (member_stats['money']))

            begs = [f"You robbed {member.mention} out of {currency}{amount:,}! [POSITIVE]"] * 5 + [f"You tried robbing {member.mention}, but they ended up robbing you out of {currency}{amount:,} [ROB]"] * 2 + [f"You failed to rob {member.mention} [NEGATIVE]"] * 2

            begs_picker = random.choice(begs)
            positive_check = re.search("POSITIVE", begs_picker)
            negative_check = re.search("NEGATIVE", begs_picker)
            if positive_check:
                userstats = economy.find_one({"guildid": ctx.guild.id, "id": member_stats['id']})
                user_money = userstats['money']
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": money + int(amount)}})
                economy.update_one({"guildid": ctx.guild.id, "id": int(member_stats['id'])},
                                   {"$set": {"money": user_money - int(amount)}})
                embed = discord.Embed(description=str(begs_picker).replace("[POSITIVE]", ''), colour=embed_colour)
                await ctx.send(embed=embed)
                return
            if negative_check:
                embed = discord.Embed(description=str(begs_picker).replace("[NEGATIVE]", ''), colour=embed_colour)
                await ctx.send(embed=embed)
                return
            if not positive_check or not negative_check:
                # remove money from author and add to member
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": money - int(amount)}})
                economy.update_one({"guildid": ctx.guild.id, "id": int(member_stats['id'])},
                                   {"$set": {"money": member_stats['money'] + int(amount)}})
                embed = discord.Embed(description=str(begs_picker).replace("[ROB]", ''), colour=embed_colour)
                await ctx.send(embed=embed)
                return
        else:
            embed = discord.Embed(description=":x: You cannot rob bots!", colour=error_embed_colour)
            await ctx.send(embed=embed)
            return






def setup(client):
    client.add_cog(rob(client))