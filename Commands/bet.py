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


class Gamble(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Balance Command
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bet(self, ctx, amount=None, bet=None):
        new_amount = re.search("-", amount)
        if amount is None or new_amount:
            embed = discord.Embed(description=":x: You must state how much you want to bet!")
            await ctx.send(embed=embed)
            return
        if bet is None:
            embed = discord.Embed(description=":x: You must state if you want to bet on **Red** or **Black**")
            await ctx.send(embed=embed)
            return
        try:
            stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
            money = stats['money']
            bet_money = int(amount)
            if int(money) < int(amount):
                embed = discord.Embed(description=":x: You have insufficient funds!")
                embed.add_field(name="Balance:", value=f"`{currency}{money}`")
                await ctx.send(embed=embed)
                return
            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                               {"$set": {"money": int(money) - int(amount)}})
            if bet.lower() == "red":
                embed = discord.Embed(title=f"Betting Machine | {currency}{amount} on {bet.upper()}")
                embed.set_footer(text=f"Member Betting: {ctx.author}")
                message = await ctx.send(embed=embed)
                colour = random.choice(['⚫', '🔴'])
                for i in range(1, 4):
                    embed.add_field(name=f"Slot {i}:", value=f"{colour}")
                await message.edit(embed=embed)
                if colour == "🔴":
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money + bet_money}})
                    embed.add_field(name="WINNER!", value=f"You won `{currency}{bet_money}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money + int(bet_money)}`")
                    await message.edit(embed=embed)
                else:
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money - bet_money}})
                    embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet_money}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money - int(bet_money)}`")
                    await message.edit(embed=embed)
                    return
            elif bet.lower() == "black":
                embed = discord.Embed(title=f"Betting Machine | {currency}{amount} on {bet.upper()}")
                embed.set_footer(text=f"Member Betting: {ctx.author}")
                message = await ctx.send(embed=embed)
                colour = random.choice(['⚫', '🔴'])
                for i in range(1, 4):
                    embed.add_field(name=f"Slot {i}:", value=f"{colour}")
                await message.edit(embed=embed)
                if colour == "⚫":
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money + bet_money}})
                    embed.add_field(name="WINNER!", value=f"You won `{currency}{bet_money}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money + int(bet_money)}`")
                    await message.edit(embed=embed)
                else:
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money - bet_money}})
                    embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet_money}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money - int(bet_money)}`")
                    await message.edit(embed=embed)
                    return

            else:
                embed = discord.Embed(description=":x: You must state if you want to bet on **Red** or **Black**")
                await ctx.send(embed=embed)
                return





        except Exception as e:
            embed = discord.Embed(description=":x: You must enter a valid number to bet on!")
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Gamble(client))
