import asyncio
import datetime
import random
import re

import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, success_embed_colour, error_embed_colour

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Crime(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Crime Commands
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command()
    async def crime(self, ctx):
        crime_array = ["Murder", "Pick Pocket", "Graffiti", "Fraud", "Arson"]
        random.shuffle(crime_array)

        # Divide the highest risk by 2!
        risk = random.randint(100, 5000)

        crime_a = crime_array[1]
        crime_b = crime_array[2]
        crime_c = crime_array[3]

        embed = discord.Embed(title="What crime would you like to commit?",
                              description=f"*Pick an option below to commit one!*\n🇦: {crime_a}\n🇧: {crime_b}\n🇨: {crime_c}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("🇦")
        await message.add_reaction("🇧")
        await message.add_reaction("🇨")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🇦", "🇧", "🇨"]

        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=15.0, check=check)

            if str(reaction.emoji) == "🇦":
                await message.remove_reaction(reaction, user)
                crime = crime_a
                if crime == "Murder":
                    messages = [
                        f"[POSITIVE] You successfully murdered an innocent pedestrian and stole `{currency}{risk:,}`"] * 5 + [f"[NEGATIVE] You killed a nearby pedestrian, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed MURDER",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Pick Pocket":
                    await message.remove_reaction(reaction, user)
                    messages = [f"[POSITIVE] You successfully picked pocketed `{currency}{risk:,}` from a stranger!"] * 5 + [f"[NEGATIVE] You were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed PICK POCKET",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Graffiti":
                    messages = [
                        f"[POSITIVE] You successfully vandalized a nearby building and were given `{currency}{risk:,}` by a kind stranger!"] * 5 + [f"[NEGATIVE] You vandalized a nearby building, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed VANDALISM",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Fraud":

                    messages = [f"[POSITIVE] You successfully lied to an old women and stole`{currency}{risk:,}`!"] * 5 + [f"[NEGATIVE] You accidentally called the police and were fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed FRAUD",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Arson":
                    messages = [
                        f"[POSITIVE] You successfully burned down a nearby building and escaped with `{currency}{risk:,}`"] * 5 + [f"[NEGATIVE] You burned down a nearby building, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed ARSON",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)

            elif str(reaction.emoji) == "🇧":
                await message.remove_reaction(reaction, user)
                crime = crime_b
                if crime == "Murder":
                    messages = [
                        f"[POSITIVE] You successfully murdered an innocent pedestrian and stole `{currency}{risk:,}`"] * 5 + [f"[NEGATIVE] You killed a nearby pedestrian, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed MURDER",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Pick Pocket":
                    messages = [f"[POSITIVE] You successfully picked pocketed `{currency}{risk:,}` from a stranger!"] * 5 + [f"[NEGATIVE] You were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed PICK POCKET",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Graffiti":
                    messages = [
                        f"[POSITIVE] You successfully vandalized a nearby building and were given `{currency}{risk:,}` by a kind stranger!"] * 5 + [f"[NEGATIVE] You vandalized a nearby building, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed VANDALISM",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Fraud":

                    messages = [f"[POSITIVE] You successfully lied to an old women and stole`{currency}{risk:,}`!"] * 5 + [f"[NEGATIVE] You accidentally called the police and were fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed FRAUD",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Arson":
                    messages = [
                        f"[POSITIVE] You successfully burned down a nearby building and escaped with `{currency}{risk:,}`"] * 5 + [f"[NEGATIVE] You burned down a nearby building, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed ARSON",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)

            elif str(reaction.emoji) == "🇨":
                crime = crime_c
                if crime == "Murder":
                    messages = [
                        f"[POSITIVE] You successfully murdered an innocent pedestrian and stole `{currency}{risk:,}`"] * 5 + [f"[NEGATIVE] You killed a nearby pedestrian, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed MURDER",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Pick Pocket":
                    messages = [f"[POSITIVE] You successfully picked pocketed `{currency}{risk:,}` from a stranger!"] * 5 + [f"[NEGATIVE] You were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed PICK POCKET",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Graffiti":
                    messages = [
                        f"[POSITIVE] You successfully vandalized a nearby building and were given `{currency}{risk:,}` by a kind stranger!"] * 5 + [f"[NEGATIVE] You vandalized a nearby building, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed VANDALISM",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Fraud":

                    messages = [f"[POSITIVE] You successfully lied to an old women and stole`{currency}{risk:,}`!"] * 5 + [f"[NEGATIVE] You accidentally called the police and were fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed FRAUD",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)
                elif crime == "Arson":
                    messages = [
                        f"[POSITIVE] You successfully burned down a nearby building and escaped with `{currency}{risk:,}`"] * 5 + [f"[NEGATIVE] You burned down a nearby building, but you were caught and fined `{currency}{risk * 2:,}`"] * 2
                    set_message = random.choice(messages)
                    embed = discord.Embed(title=f"{ctx.author.name} committed ARSON",
                                          description=set_message.replace("[POSITIVE]", "").replace("[NEGATIVE]", ""))
                    check = re.search(r"POSITIVE", set_message)
                    if check:
                        # give money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": risk}})
                        embed.colour = success_embed_colour
                    else:
                        # take money
                        economy.update_one(
                            {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                            {"$inc": {"money": -risk * 2}})
                        embed.colour = error_embed_colour
                        money = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                        embed.add_field(name="Balance:", value=f"`{currency}{money['money']:,}`")
                    await message.edit(embed=embed)




        except asyncio.TimeoutError:
            embed = discord.Embed(description=":x: You took too long to choose a crime!")
            embed.colour = error_embed_colour
            await message.edit(embed=embed)


def setup(client):
    client.add_cog(Crime(client))
