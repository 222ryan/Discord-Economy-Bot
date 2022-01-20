import asyncio
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
    async def bet(self, ctx, amount: int = None, bet=None):
        try:
            if amount is None:
                embed = discord.Embed(description=":x: You must state how much you want to bet!")
                await ctx.send(embed=embed)
                return
            if bet is None:
                embed = discord.Embed(description=":x: You must state if you want to bet on **Red** or **Black**")
                await ctx.send(embed=embed)
                return
            if amount > config['black_red_cap']:
                embed = discord.Embed(description=f":x: **Betting Machine** only supports bets up to `{currency}{config['black_red_cap']:,}`!")
                await ctx.send(embed=embed)
                return
            stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
            money = stats['money']
            bet_money = int(amount)
            if int(money) < int(amount):
                embed = discord.Embed(description=":x: You have insufficient funds!")
                embed.add_field(name="Balance:", value=f"`{currency}{money}:,`")
                await ctx.send(embed=embed)
                return
            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                               {"$set": {"money": int(money) - int(amount)}})
            if bet.lower() == "red":
                embed = discord.Embed(title=f"Betting Machine | {currency}{amount:,} on {bet.upper()}")
                embed.set_footer(text=f"Member Betting: {ctx.author}")
                message = await ctx.send(embed=embed)
                colour = random.choice(['⚫', '🔴'])
                for i in range(1, 4):
                    embed.add_field(name=f"Slot {i}:", value=f"{colour}")
                await message.edit(embed=embed)
                if colour == "🔴":
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money + bet_money}})
                    embed.add_field(name="WINNER!", value=f"You won `{currency}{bet_money:,}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money + int(bet_money):,}`")
                    await message.edit(embed=embed)
                else:
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money - bet_money}})
                    embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet_money:,}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money - int(bet_money):,}`")
                    await message.edit(embed=embed)
                    return
            elif bet.lower() == "black":
                embed = discord.Embed(title=f"Betting Machine | {currency}{amount:,} on {bet.upper()}")
                embed.set_footer(text=f"Member Betting: {ctx.author}")
                message = await ctx.send(embed=embed)
                colour = random.choice(['⚫', '🔴'])
                for i in range(1, 4):
                    embed.add_field(name=f"Slot {i}:", value=f"{colour}")
                await message.edit(embed=embed)
                if colour == "⚫":
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money + bet_money}})
                    embed.add_field(name="WINNER!", value=f"You won `{currency}{bet_money:,}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money + int(bet_money):,}`")
                    await message.edit(embed=embed)
                else:
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"money": money - bet_money}})
                    embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet_money:,}`")
                    embed.add_field(name="Balance:", value=f"`{currency}{money - int(bet_money):,}`")
                    await message.edit(embed=embed)
                    return

            else:
                embed = discord.Embed(description=":x: You must state if you want to bet on **Red** or **Black**")
                await ctx.send(embed=embed)
                return





        except Exception as e:
            embed = discord.Embed(description=":x: You must enter a valid number to bet on!")
            await ctx.send(embed=embed)
            raise e


    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.command()
    async def highlow(self, ctx, bet: int = None):
        try:
            if bet is None or bet < 0:
                embed = discord.Embed(description=":x: You must enter a number to bet on!")
                await ctx.send(embed=embed)
                return
            if bet > config['high_low_cap']:
                embed = discord.Embed(description=f":x: **High/Low** only supports bets up to `{currency}{config['high_low_cap']:,}`!")
                await ctx.send(embed=embed)
                return
            stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
            money = stats["money"]
            if money < int(bet):
                embed = discord.Embed(description=":x: You do not have enough money to bet that amount!")
                await ctx.send(embed=embed)
                return
            bet = int(bet)
            number = random.randint(1, 100)
            hint_num = random.randint(1, number)

            embed = discord.Embed(title=f"High/Low | {ctx.author.name}",
                                  description=f"I just chose a secret number between `1 and 100`. \nIs the secret number higher or lower than **{hint_num}**")
            message = await ctx.send(embed=embed)

            await message.add_reaction("⬆️")
            await message.add_reaction("💣")
            await message.add_reaction("⬇️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬆️", "⬇️", "💣"]

            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

                    if str(reaction.emoji) == "⬆️":
                        if number > hint_num:
                            embed = discord.Embed(title=f"High/Low | {ctx.author.name} | HIGHER",
                                                  description=f"The secret number was **{number}**")
                            embed.set_footer(text=f"Member Betting: {ctx.author}")
                            await message.edit(embed=embed)
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                               {"$set": {"money": money + int(bet)}})
                            embed.add_field(name="WINNER!", value=f"You won `{currency}{bet:,}`")
                            embed.add_field(name="Balance:", value=f"`{currency}{money + bet:,}`")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=f"High/Low | {ctx.author.name} | HIGHER",
                                                  description=f"The secret number was **{number}**")
                            embed.set_footer(text=f"Member Betting: {ctx.author}")
                            await message.edit(embed=embed)
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                               {"$set": {"money": money - 100}})
                            embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet:,}`")
                            embed.add_field(name="Balance:", value=f"`{currency}{money - int(bet):,}`")
                            await message.edit(embed=embed)
                        await message.edit(embed=embed)
                        await message.remove_reaction(reaction, user)
                        return
                    elif str(reaction.emoji) == "⬇️":
                        if number < hint_num:
                            embed = discord.Embed(title=f"High/Low | {ctx.author.name} | LOWER",
                                                  description=f"The secret number was **{number:,}**")
                            embed.set_footer(text=f"Member Betting: {ctx.author}")
                            await message.edit(embed=embed)
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                               {"$set": {"money": money + int(bet)}})
                            embed.add_field(name="WINNER!", value=f"You won `{currency}{bet:,}`")
                            embed.add_field(name="Balance:", value=f"`{currency}{money + bet:,}`")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=f"High/Low | {ctx.author.name} | LOWER",
                                                  description=f"The secret number was **{number}**")
                            embed.set_footer(text=f"Member Betting: {ctx.author}")
                            await message.edit(embed=embed)
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                               {"$set": {"money": money - int(bet)}})
                            embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet:,}`")
                            embed.add_field(name="Balance:", value=f"`{currency}{money - bet:,}`")
                            await message.edit(embed=embed)
                        await message.remove_reaction(reaction, user)
                    elif str(reaction.emoji) == "💣":
                        if number == hint_num:
                            embed = discord.Embed(title=f"High/Low | {ctx.author.name} | EXACT",
                                                  description=f"The secret number was **{number}**")
                            embed.set_footer(text=f"Member Betting: {ctx.author}")
                            await message.edit(embed=embed)
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                               {"$set": {"money": money + int(bet * 2)}})
                            embed.add_field(name="WINNER!", value=f"You won `{currency}{bet * 2:,}`")
                            embed.add_field(name="Balance:", value=f"`{currency}{money + (bet*2):,}`")
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=f"High/Low | {ctx.author.name} | EXACT",
                                                  description=f"The secret number was **{number}**")
                            embed.set_footer(text=f"Member Betting: {ctx.author}")
                            await message.edit(embed=embed)
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                               {"$set": {"money": money - int(bet*2)}})
                            embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet*2:,}`")
                            embed.add_field(name="Balance:", value=f"`{currency}{money - (bet*2):,}`")
                            await message.edit(embed=embed)
                    else:
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.delete()
                    break
        except Exception as e:
            embed = discord.Embed(description=":x: You need to enter a valid amount to bet on!")
            await ctx.send(embed=embed)
            raise e


    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command()
    async def slots(self, ctx, bet: int = None):
        try:
            if bet is None or bet < 0:
                embed = discord.Embed(description=":x: You need to enter a valid amount to bet on!")
                await ctx.send(embed=embed)
                return
            if bet > economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["money"]:
                embed = discord.Embed(description=":x: You don't have enough money to bet that much!")
                await ctx.send(embed=embed)
                return
            if bet > config['slots_cap']:
                embed = discord.Embed(description=f":x: **Slots** only supports bets up to `{currency}{config['slots_cap']:,}`")
                await ctx.send(embed=embed)
                return
            slots = ["🍊", "🍐", "🍋", "🍉", "🍇", "🍓", "🍒", "🍍"]
            slots1 = random.choice(slots)
            slots2 = random.choice(slots)
            slots3 = random.choice(slots)
            embed = discord.Embed(title=f"SLOTS MACHINE | {ctx.author.name}",
                                  description=f"```  {random.choice(slots)} | {random.choice(slots)} | {random.choice(slots)}\n"
                                              f"→ {slots1} | {slots2} | {slots3} ←\n"
                                              f"  {random.choice(slots)} | {random.choice(slots)} | {random.choice(slots)}```")
            embed.set_footer(text=f"Member Betting: {ctx.author}")
            message = await ctx.send(embed=embed)
            if slots1 == slots2 and slots2 == slots3:
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})[
                                                          "money"] + int(bet * 2)}})
                embed.add_field(name="$$ JACKPOT $$", value=f"You won `"
                                                            f"{currency}{bet * 2:,}`")
                embed.add_field(name="Balance:",
                                value=f'`{currency}{economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["money"]:,}`')
                await message.edit(embed=embed)
            elif slots1 == slots2 or slots2 == slots3 or slots1 == slots3:
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})[
                                                          "money"] + int(bet)}})
                embed.add_field(name="$$ GREAT $$", value=f"You won `{currency}{bet:,}`")
                embed.add_field(name="Balance:",
                                value=f'`{currency}{economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["money"]:,}`')
                await message.edit(embed=embed)
            else:
                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                   {"$set": {"money": economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})[
                                                          "money"] - int(bet)}})
                embed.add_field(name="LOSS!", value=f"You lost `{currency}{bet:,}`")
                embed.add_field(name="Balance:",
                                value=f'`{currency}{economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["money"]:,}`')
                await message.edit(embed=embed)



        except Exception as e:
            embed = discord.Embed(description=":x: You need to enter a valid amount to bet on!")
            await ctx.send(embed=embed)
            raise e






def setup(client):
    client.add_cog(Gamble(client))
