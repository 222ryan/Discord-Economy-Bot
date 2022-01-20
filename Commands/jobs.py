import asyncio
import time

import discord
from discord.ext import commands, tasks
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, embed_colour, error_embed_colour, success_embed_colour

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Jobs(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Balance Command
    @commands.command(aliases=['job'])
    async def jobs(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id, "job_type": {"$exists": False}})
        if stats['job'] == "None":
            embed = discord.Embed(title="🏢 JOBS CENTRE")
            embed.add_field(name="Job Status:", value="`Unemployed`")
            embed.add_field(name="Available Jobs",
                            value=f"```🛒 Shop Owner - Requires {currency}{config['shop_money_requirement']:,} and x1 Stock with a Medium Pay\n🎣 Fisher - Requires {currency}{config['fisher_money_requirement']:,} and x1 Fishing Rod with a Medium Pay\n🖥️ Programmer - Requires {currency}{config['programmer_money_requirement']:,}, x1 Computer, x1 IDE License, x1 Server with a Large Pay\n🐶 Dog Walker - Requires {currency}{config['dog_money_requirement']:,} with a Low Pay```",
                            inline=False)
            embed.set_footer(text=f"Want a job? - {config['Prefix']}apply <jobName> to apply!")
            await ctx.send(embed=embed)
            return
        if member:
            member_stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id, "job_type": {"$exists": False}})
            if member_stats['job'] == "None":
                embed = discord.Embed(title="🏢 JOBS CENTRE",
                                      description=f"{member.mention} is currently `Unemployed`!")
                await ctx.send(embed=embed)
                return
            else:
                job_stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id, "job_type": {"$exists": True}})
                embed = discord.Embed(title=f"💼 {member}'s Job")
                embed.add_field(name="Job:", value=f"`{member_stats['job']}`")
                if job_stats['job_type'] == "Shop":
                    embed.add_field(name="Daily Income:", value=f"`{currency}{member_stats['daily_income']:,}`")
                    if "Stock" in member_stats['inventory']:
                        embed.add_field(name="Stocked?", value="`✅`")
                    else:
                        embed.add_field(name="Stocked?", value="`❌`")
                if job_stats['job_type'] == "Fisher":
                    embed.add_field(name="Daily Income:", value=f"`{currency}{member_stats['daily_income']:,}`")
                    if "Fishing Rod" in member_stats['inventory']:
                        embed.add_field(name="Fishing Rod Stocked?", value="`✅`")
                    else:
                        embed.add_field(name="Fishing Rod Stocked?", value="`❌`")

                if job_stats['job_type'] == "Programmer":
                    embed.add_field(name="Daily Income:", value=f"`{currency}{member_stats['daily_income']:,}`")
                    if "Ide License" in member_stats['inventory']:
                        embed.add_field(name="IDE License Stocked?", value="`✅`")
                    else:
                        embed.add_field(name="IDE License Stocked?", value="`❌`")

                if job_stats['job_type'] == "Dog Walker":
                    embed.add_field(name="Daily Income:", value=f"`{currency}{member_stats['daily_income']:,}`")
                    if "Leash" in member_stats['inventory']:
                        embed.add_field(name="Leash Stocked?", value="`✅`")
                    else:
                        embed.add_field(name="Leash Stocked?", value="`❌`")

                dashes = 10
                level = job_stats['level']
                max_level = 10
                partone_dashConvert = int(
                    max_level / dashes)
                current_dash = int(level / partone_dashConvert)
                remaining_dash = dashes - current_dash
                percent = int((level / max_level) * 100)
                Display = '⬜' * current_dash
                remainingDisplay = '⬛' * remaining_dash
                embed.add_field(name=f"Level ({job_stats['level']}/10):",
                                value=f"{Display + remainingDisplay} {percent}%", inline=False)
                await ctx.send(embed=embed)

    @commands.command()
    async def apply(self, ctx, *, job: str):
        stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
        if stats['job'] == "None":
            if job.lower() == "shop owner":
                if stats['money'] >= config['shop_money_requirement']:
                    if "Stock" in stats['inventory']:
                        # set the users job to the job they have applied for
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$set": {"job": "Shop", "daily_income": config['starting_shop_income']}})
                        # remove the users stock from their inventory
                        count = 0
                        for x in stats['inventory']:
                            count += 1
                            if x == "Stock":
                                # take away 1 from inventory amount where count
                                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                                   {"$inc": {"inventory_amount." + str(count - 1): - 1}})
                                if economy.find_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}})[
                                    "inventory_amount"][
                                    count - 1] == 0:
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                        {"$pull": {"inventory": "Stock"}})
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                        {"$pull": {"inventory_amount": 0}})
                                break
                        # add the job to the database
                        new_job = {
                            "guildid": ctx.guild.id,
                            "id": ctx.author.id,
                            "job_type": "Shop",
                            "level": 1,
                            "last_pay": None}
                        economy.insert_one(new_job)
                        # remove the users money from their account
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$inc": {"money": -config['shop_money_requirement']}})
                        embed = discord.Embed(title="🏢 JOBS CENTRE",
                                              description=f"{ctx.author.mention} has applied for the `{job.title()}` job!")
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(description=":x: You do not own any stock!", colour=error_embed_colour)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=":x: You do not have enough money to become a Shop Owner!",
                                          colour=error_embed_colour)
                    await ctx.send(embed=embed)
            elif job.lower() == "fisher":
                if stats['money'] >= config['fisher_money_requirement']:
                    if "Fishing Rod" in stats['inventory']:
                        # set the users job to the job they have applied for
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$set": {"job": "Fisher",
                                                     "daily_income": config['starting_fisher_income']}})
                        # remove the users fishing rod from their inventory
                        count = 0
                        for x in stats['inventory']:
                            count += 1
                            if str(x).title() == "Fishing Rod".title():
                                # take away 1 from inventory amount where count
                                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                                   {"$inc": {"inventory_amount." + str(count - 1): - 1}})
                                if economy.find_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}})[
                                    "inventory_amount"][
                                    count - 1] == 0:
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                        {"$pull": {"inventory": "Fishing Rod"}})
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                        {"$pull": {"inventory_amount": 0}})
                                break

                            # add the job to the database

                        new_job = {
                            "guildid": ctx.guild.id,
                            "id": ctx.author.id,
                            "job_type": "Fisher",
                            "level": 1,
                            "last_pay": None}
                        economy.insert_one(new_job)
                        # remove the users money from their account
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$inc": {"money": -config['fisher_money_requirement']}})
                        embed = discord.Embed(title="🏢 JOBS CENTRE",
                                              description=f"{ctx.author.mention} has applied for the `{job.title()}` job!")
                        await ctx.send(embed=embed)

                    else:
                        embed = discord.Embed(description=":x: You do not own a Fishing Rod!",
                                              colour=error_embed_colour)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=":x: You do not have enough money to become a Fisher!",
                                          colour=error_embed_colour)
                    await ctx.send(embed=embed)
            elif job.lower() == "programmer":
                if stats['money'] >= config['programmer_money_requirement']:
                    if "Computer" in stats['inventory']:
                        if "Ide License".title() in stats['inventory']:
                            if "Server" in stats['inventory']:
                                # set the users job to the job they have applied for
                                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                                   {"$set": {"job": "Programmer",
                                                             "daily_income": config['starting_programmer_income']}})
                                # remove the users computer from their inventory
                                count = 0
                                for x in stats['inventory']:
                                    count += 1
                                    if str(x).title() == "Ide License".title():
                                        # take away 1 from inventory amount where count
                                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                                           {"$inc": {"inventory_amount." + str(count - 1): - 1}})
                                        if economy.find_one(
                                                {"guildid": ctx.guild.id, "id": ctx.author.id,
                                                 "job_type": {"$exists": False}})[
                                            "inventory_amount"][
                                            count - 1] == 0:
                                            economy.update_one(
                                                {"guildid": ctx.guild.id, "id": ctx.author.id,
                                                 "job_type": {"$exists": False}},
                                                {"$pull": {"inventory": "Ide License"}})
                                            economy.update_one(
                                                {"guildid": ctx.guild.id, "id": ctx.author.id,
                                                 "job_type": {"$exists": False}},
                                                {"$pull": {"inventory_amount": 0}})
                                        break

                                # add the job to the database
                                new_job = {
                                    "guildid": ctx.guild.id,
                                    "id": ctx.author.id,
                                    "job_type": "Programmer",
                                    "level": 1,
                                    "last_pay": None}
                                economy.insert_one(new_job)

                                # remove the users money
                                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                                   {"$inc": {"money": - config['programmer_money_requirement']}})
                                embed = discord.Embed(title="🏢 JOBS CENTRE",
                                                      description=f"{ctx.author.mention} has applied for the `{job.title()}` job!")
                                await ctx.send(embed=embed)
                                return
                            else:
                                embed = discord.Embed(description=f":x: {ctx.author.mention} You do not own a Server!", colour=error_embed_colour)
                                await ctx.send(embed=embed)
                                return
                        else:
                            embed = discord.Embed(description=f":x: {ctx.author.mention} You do not own an IDE License!", colour=error_embed_colour)
                            await ctx.send(embed=embed)
                            return
                    else:
                        embed = discord.Embed(description=f":x: {ctx.author.mention} You do not own a Computer!", colour=error_embed_colour)
                        await ctx.send(embed=embed)
                        return
                else:
                    embed = discord.Embed(
                        description=f":x: {ctx.author.mention} You do not have enough money to become a Programmer!", colour=error_embed_colour)
                    await ctx.send(embed=embed)
                    return
            elif job.lower() == "dog walker":
                if stats['money'] >= config['dog_money_requirement']:
                    if "Leash" in stats['inventory']:
                        # set the users job to the job they have applied for
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$set": {"job": "Dog Walker",
                                                     "daily_income": config['starting_dog_income']}})
                        count = 0
                        for x in stats['inventory']:
                            count += 1
                            if str(x).title() == "Leash".title():
                                # take away 1 from inventory amount where count
                                economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                                   {"$inc": {"inventory_amount." + str(count - 1): - 1}})
                                if economy.find_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id,
                                         "job_type": {"$exists": False}})[
                                    "inventory_amount"][
                                    count - 1] == 0:
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id,
                                         "job_type": {"$exists": False}},
                                        {"$pull": {"inventory": "Leash"}})
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id,
                                         "job_type": {"$exists": False}},
                                        {"$pull": {"inventory_amount": 0}})
                                break

                        # add the job to the database
                        new_job = {
                            "guildid": ctx.guild.id,
                            "id": ctx.author.id,
                            "job_type": "Dog Walker",
                            "level": 1,
                            "last_pay": None}
                        economy.insert_one(new_job)

                        # remove the users money
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$inc": {"money": - config['dog_money_requirement']}})
                        embed = discord.Embed(title="🏢 JOBS CENTRE",
                                              description=f"{ctx.author.mention} has applied for the `{job.title()}` job!")
                        await ctx.send(embed=embed)
                        return
                    else:
                        embed = discord.Embed(description=f":x: {ctx.author.mention} You do not own a Leash!",
                                              colour=error_embed_colour)
                        await ctx.send(embed=embed)
                        return
                else:
                    embed = discord.Embed(
                        description=f":x: {ctx.author.mention} You do not have enough money to become a Dog Walker!",
                        colour=error_embed_colour)
                    await ctx.send(embed=embed)
                    return

        else:
            embed = discord.Embed(description=f":x: {ctx.author.mention} You already have a job!", color=error_embed_colour)
            embed.set_footer(text=f"{config['Prefix']}quitjob to quit your current job!")
            await ctx.send(embed=embed)
            return

    @commands.command()
    async def quitjob(self, ctx):
        stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
        if stats['job'] == "None":
            embed = discord.Embed(description=":x: You do not have a Job!")
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"{stats['job']} Retirement",
                              description="Are you sure you want to quit your job? This cannot be undone and any progress will be deleted!")
        message = await ctx.send(embed=embed)

        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

                if str(reaction.emoji) == "✅":
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"job": "None", "daily_income": 0}})
                    economy.delete_one({"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": True}})
                    embed = discord.Embed(description="✅ You no longer work!")
                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction, user)
                    await asyncio.sleep(2)
                    await message.delete()
                    return
                elif str(reaction.emoji) == "❌":
                    await message.remove_reaction(reaction, user)
                    await message.delete()
                else:
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.delete()
                break


def setup(client):
    client.add_cog(Jobs(client))

    @tasks.loop(seconds=10)
    async def add_daily_income():
        for guild in client.guilds:
            for member in guild.members:
                for user in economy.find({"guildid": guild.id, "id": member.id, "job_type": {"$exists": True}}):
                    if user['job_type'] == "Shop":
                        if user["last_pay"] is None or user['last_pay'] + 86400 < int(time.time()):
                            economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Shop"},
                                               {"$set": {"last_pay": int(time.time())}})
                            owner = economy.find_one(
                                {"guildid": guild.id, "id": member.id, "job_type": {"$exists": False}})
                            if "Stock" not in owner['inventory']:
                                channel = await member.create_dm()
                                embed = discord.Embed(title="🛒 Shop Owner Payment Failed",
                                                      description=f"You have not bought any `Stock`!",
                                                      colour=error_embed_colour)
                                embed.set_footer(text=f"From Server: {guild}")
                                await channel.send(embed=embed)
                                return
                            if user['level'] != 10:
                                level = user['level'] + 1
                                daily_income = config['starting_shop_income'] * level
                            else:
                                daily_income = config['starting_shop_income'] * user['level']
                            economy.update_one({"guildid": guild.id, "id": member.id},
                                               {"$inc": {"money": daily_income}})
                            count = 0
                            for x in owner['inventory']:
                                if x == "Stock":
                                    for i in owner['inventory_amount']:
                                        count += 1
                                        if i == count - 1:
                                            # remove 1 from the inventory_amount where count is in the array
                                            check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                      "inventory_amount." + str(count - 1): {
                                                                          "$exists": True}})
                                            if check:
                                                economy.update_one({"guildid": guild.id, "id": member.id},
                                                                   {"$inc": {"inventory_amount." + str(count - 1): -1}})
                                                check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                          "inventory_amount." + str(count - 1): {
                                                                              "$exists": True}})
                                                get_num = check['inventory_amount'][count - 1]
                                                print(get_num)
                                                if get_num < 1:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory": "Stock"}})
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory_amount": 0}})
                                                else:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$inc": {
                                                                           "inventory_amount." + str(count - 1): - 1}})
                                                    continue

                                    break

                            channel = await member.create_dm()
                            embed = discord.Embed(title="🛒 Shop Owner Payment",
                                                  description=f"You have been paid {currency}{daily_income:,} for "
                                                              f"working as a `Shop Owner`")
                            money = economy.find_one({"guildid": guild.id, "id": member.id})
                            embed.add_field(name="Balance", value=f"`{currency}{money['money']:,}`")
                            embed.set_footer(text=f"From Server: {guild}")
                            if user['level'] != 10:
                                embed.add_field(name="LEVEL UP!",
                                                value=f"`Your shop is now Level: {user['level'] + 1}/10`")
                                economy.update_one({"guildid":guild.id, "id": member.id, "job_type": "Shop"},
                                                   {"$set": {"level": user['level'] + 1}})
                            await channel.send(embed=embed)
                    elif user['job_type'] == "Fisher":
                        if user["last_pay"] is None or user['last_pay'] + 86400 < int(time.time()):
                            economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Fisher"},
                                               {"$set": {"last_pay": int(time.time())}})
                            owner = economy.find_one(
                                {"guildid": guild.id, "id": member.id, "job_type": {"$exists": False}})
                            if "Fishing Rod" not in owner['inventory']:
                                channel = await member.create_dm()
                                embed = discord.Embed(title="🎣 Fisher Payment Failed",
                                                      description=f"You have not bought a `Fishing Rod`!",
                                                      colour=error_embed_colour)
                                embed.set_footer(text=f"From Server: {guild}")
                                await channel.send(embed=embed)
                                return
                            if user['level'] != 10:
                                level = user['level'] + 1
                                daily_income = config['starting_fisher_income'] * level
                            else:
                                daily_income = config['starting_shop_income'] * user['level']
                            economy.update_one({"guildid": user['guildid'], "id": user['id']},
                                               {"$inc": {"money": daily_income}})
                            count = 0
                            for x in owner['inventory']:
                                if x == "Fishing Rod":
                                    for i in owner['inventory_amount']:
                                        count += 1
                                        if i == count - 1:
                                            check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                      "inventory_amount." + str(count - 1): {
                                                                          "$exists": True}})
                                            if check:
                                                economy.update_one({"guildid": guild.id, "id": member.id},
                                                                   {"$inc": {"inventory_amount." + str(count - 1): -1}})
                                                check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                          "inventory_amount." + str(count - 1): {
                                                                              "$exists": True}})
                                                get_num = check['inventory_amount'][count - 1]
                                                if get_num < 1:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory": "Stock"}})
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory_amount": 0}})
                                                else:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$inc": {
                                                                           "inventory_amount." + str(count - 1): - 1}})
                                                    continue
                                    break

                            channel = await member.create_dm()
                            embed = discord.Embed(title="🎣 Fisher Payment",
                                                  description=f"You have been paid {currency}{daily_income:,} for "
                                                              f"working as a `Fisher`")
                            money = economy.find_one({"guildid": guild.id, "id": member.id})
                            embed.add_field(name="Balance", value=f"`{currency}{money['money']:,}`")
                            embed.set_footer(text=f"From Server: {guild}")
                            if user['level'] != 10:
                                embed.add_field(name="LEVEL UP!",
                                                value=f"`Your Job is now Level: {user['level'] + 1}/10`")
                                economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Fisher"},
                                                   {"$set": {"level": user['level'] + 1}})
                            await channel.send(embed=embed)
                    elif user['job_type'] == "Programmer":
                        if user["last_pay"] is None or user['last_pay'] + 86400 < int(time.time()):
                            economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Programmer"},
                                               {"$set": {"last_pay": int(time.time())}})
                            owner = economy.find_one(
                                {"guildid": guild.id, "id": member.id, "job_type": {"$exists": False}})
                            if "Ide License" not in owner['inventory']:
                                channel = await member.create_dm()
                                embed = discord.Embed(title="💻 Programmer Payment Failed",
                                                      description=f"You have not bought an `Ide License`!", colour=error_embed_colour)
                                embed.set_footer(text=f"From Server: {guild}")
                                await channel.send(embed=embed)
                                return
                            if user['level'] != 10:
                                level = user['level'] + 1
                                daily_income = config['starting_programmer_income'] * level
                            else:
                                daily_income = config['starting_shop_income'] * user['level']
                            economy.update_one({"guildid": guild.id, "id": member.id},
                                               {"$inc": {"money": daily_income}})
                            count = 0
                            for x in owner['inventory']:
                                if x == "Ide License":
                                    for i in owner['inventory_amount']:
                                        count += 1
                                        if i == count - 1:
                                            check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                      "inventory_amount." + str(count - 1): {
                                                                          "$exists": True}})
                                            if check:
                                                economy.update_one({"guildid": guild.id, "id": member.id},
                                                                   {"$inc": {"inventory_amount." + str(count - 1): -1}})
                                                check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                          "inventory_amount." + str(count - 1): {
                                                                              "$exists": True}})
                                                get_num = check['inventory_amount'][count - 1]
                                                if get_num < 1:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory": "Ide License"}})
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory_amount": 0}})
                                                else:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$inc": {
                                                                           "inventory_amount." + str(count - 1): - 1}})
                                                    continue
                                    break

                            channel = await member.create_dm()
                            embed = discord.Embed(title="🖥️ Programmer Payment",
                                                  description=f"You have been paid {currency}{daily_income:,} for "
                                                              f"working as a `Programmer`")
                            money = economy.find_one({"guildid": guild.id, "id": member.id})
                            embed.add_field(name="Balance", value=f"`{currency}{money['money']:,}`")
                            embed.set_footer(text=f"From Server: {guild}")
                            if user['level'] != 10:
                                embed.add_field(name="LEVEL UP!",
                                                value=f"`Your Job is now Level: {user['level'] + 1}/10`")
                                economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Programmer"},
                                                   {"$set": {"level": user['level'] + 1}})
                            await channel.send(embed=embed)
                    elif user['job_type'] == "Dog Walker":
                        if user["last_pay"] is None or user['last_pay'] + 86400 < int(time.time()):
                            economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Dog Walker"},
                                               {"$set": {"last_pay": int(time.time())}})
                            owner = economy.find_one(
                                {"guildid": guild.id, "id": member.id, "job_type": {"$exists": False}})
                            if "Leash" not in owner['inventory']:
                                channel = await member.create_dm()
                                embed = discord.Embed(title="🐶 Dog Walker Payment Failed",
                                                      description=f"You have not bought a `Leash`!", colour=error_embed_colour)
                                embed.set_footer(text=f"From Server: {guild}")
                                await channel.send(embed=embed)
                                return
                            if user['level'] != 10:
                                level = user['level'] + 1
                                daily_income = config['starting_dog_income'] * level
                            else:
                                daily_income = config['starting_shop_income'] * user['level']
                            economy.update_one({"guildid": guild.id, "id": member.id},
                                               {"$inc": {"money": daily_income}})
                            count = 0
                            for x in owner['inventory']:
                                if x == "Leash":
                                    for i in owner['inventory_amount']:
                                        count += 1
                                        if i == count - 1:
                                            check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                      "inventory_amount." + str(count - 1): {
                                                                          "$exists": True}})
                                            if check:
                                                economy.update_one({"guildid": guild.id, "id": member.id},
                                                                   {"$inc": {"inventory_amount." + str(count - 1): -1}})
                                                check = economy.find_one({"guildid": guild.id, "id": member.id,
                                                                          "inventory_amount." + str(count - 1): {
                                                                              "$exists": True}})
                                                get_num = check['inventory_amount'][count - 1]
                                                if get_num < 1:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory": "Leash"}})
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$pull": {"inventory_amount": 0}})
                                                else:
                                                    economy.update_one({"guildid": guild.id, "id": member.id},
                                                                       {"$inc": {
                                                                           "inventory_amount." + str(count - 1): - 1}})
                                                    continue
                                    break

                            channel = await member.create_dm()
                            embed = discord.Embed(title="🐶 Dog Walker Payment",
                                                  description=f"You have been paid {currency}{daily_income:,} for "
                                                              f"working as a `Dog Walker`")
                            money = economy.find_one({"guildid": guild.id, "id": member.id})
                            embed.add_field(name="Balance", value=f"`{currency}{money['money']:,}`")
                            embed.set_footer(text=f"From Server: {guild}")
                            if user['level'] != 10:
                                embed.add_field(name="LEVEL UP!",
                                                value=f"`Your Job is now Level: {user['level'] + 1}/10`")
                                economy.update_one({"guildid": user['guildid'], "id": user['id'], "job_type": "Dog Walker"},
                                                   {"$set": {"level": user['level'] + 1}})
                            await channel.send(embed=embed)

    add_daily_income.start()
