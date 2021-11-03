import asyncio

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
    async def jobs(self, ctx, job=None, apply=None):
        prefix = config['Prefix']
        if job is None:
            embed = discord.Embed(title=f"💼 {ctx.guild.name}'s Job Centre", description=f"Welcome to the Job "
                                                                                         f"Centre, "
                                                                                         f"{ctx.author.mention}!", colour=embed_colour)
            embed.add_field(name="Jobs:",
                            value=f"```🛒 - Shop Owner - {prefix}job shop ```")
            await ctx.send(embed=embed)
        elif job.lower() == "shop":
            if apply is None:
                embed = discord.Embed(title=f"💼 {ctx.guild.name}'s Job Centre",
                                      description="Showing information for the Job `Shop Owner`", colour=embed_colour)
                embed.add_field(name="About:", value=f"`You will own your very own Shop that generates low income (Requires: {currency}{config['shop_money_requirement']})`",
                                inline=False)
                embed.add_field(name="How to Start:", value=f"`{prefix}job shop start`")
                embed.add_field(name="Starting Daily Income", value=f"`{currency}{config['starting_shop_income']}`")
                await ctx.send(embed=embed)
            else:
                stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
                if stats['job'] != "None":
                    embed = discord.Embed(description=":x: You already have a job!", embed_colour=error_embed_colour)
                    embed.set_footer(text=f"Current Job: {stats['job']}")
                    await ctx.send(embed=embed)
                else:
                    money = stats['money']
                    if money < config['shop_money_requirement']:
                        embed = discord.Embed(description=":x: You have insufficient funds to work as a **Shop Owner**", embed_colour=error_embed_colour)
                        await ctx.send(embed=embed)
                        return
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                       {"$set": {"job": "Shop", "daily_income": config['starting_shop_income'], "money": money - config['shop_money_requirement']}})
                    newjob = {"guildid": ctx.guild.id, "id": ctx.author.id,
                              "job_type": "Shop", "level": 1, "last_pay": None}
                    economy.insert_one(newjob)
                    embed = discord.Embed(description="✅ You are now a Shop Owner!", colour=success_embed_colour)
                    embed.set_footer(text=f"Use {prefix}shop to get started!")
                    await ctx.send(embed=embed)


    @commands.command()
    async def quitjob(self, ctx):
        stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
        if stats['job'] != "Shop":
            embed = discord.Embed(description=":x: You do not have a Job!")
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title="Shop Owner Retirement",
                              description="Are you sure you want to quit being a **Shop Owner**? This cannot be undone and any progress will be deleted!")
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
                    economy.delete_one({"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": "Shop"})
                    embed = discord.Embed(description="✅ You no longer work as a **Shop Owner**!")
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

    @commands.command()
    async def shop(self, ctx, member: discord.Member = None, quit=None):
        prefix = config['Prefix']
        if member is None:
            member = ctx.author
        if quit is None:
            job_stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id, "job_type": "Shop"})
            user_stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id})
            if job_stats:
                embed = discord.Embed(title=f"🛒 {member}'s Shop")
                dashes = 10

                level = job_stats['level']
                max_level = 10  # Max Health
                partone_dashConvert = int(
                    max_level / dashes)
                current_dash = int(level / partone_dashConvert)
                remaining_dash = dashes - current_dash
                percent = int((level / max_level) * 100)
                Display = '⬜' * current_dash
                remainingDisplay = '⬛' * remaining_dash

                embed.add_field(name="Daily Income", value=f"`{currency}{user_stats['daily_income']}`", inline=False)
                embed.add_field(name=f"Level ({job_stats['level']}/10):", value=f"{Display + remainingDisplay} {percent}%", inline=False)
                await ctx.send(embed=embed)
            else:
                if member == ctx.author:
                    embed = discord.Embed(description=":x: You don't work as a Shop Owner!")
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f":x: {member.mention} doesn't work as a Shop Owner!")
                    await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Jobs(client))

    @tasks.loop(hours=24)
    async def e():
        for guild in client.guilds:
            for member in guild.members:
                if not member.bot:
                    job_stats = economy.find({"guildid": guild.id, "id": member.id, "job_type": "Shop"})
                    if job_stats:
                        for doc in job_stats:
                            if doc['last_pay'] is None:
                                channel = await member.create_dm()
                                stats = economy.find_one({"guildid": guild.id, "id": member.id})
                                money = stats['money']
                                if doc['level'] != 10:
                                    level = doc['level'] + 1
                                    daily_income = config['starting_shop_income'] * level
                                else:
                                    daily_income = config['starting_shop_income'] * 10
                                embed = discord.Embed(title="🛒 Shop Owner Payment", description=f"You have been paid {currency}{daily_income} for working as a `Shop Owner`!")
                                embed.add_field(name="Balance:", value=f"`{currency}{money + daily_income}`")
                                economy.update_one({"guildid": guild.id, "id": member.id},
                                                   {"$set": {"money": money + daily_income, "daily_income": daily_income}})
                                if doc['level'] != 10:
                                    embed.add_field(name="LEVEL UP!", value=f"Your shop is now `Level {doc['level'] + 1}`!")
                                    economy.update_one({"guildid": guild.id, "id": member.id, "job_type": "Shop"},
                                                       {"$set": {"money": money + daily_income, "level": doc['level'] + 1}})
                                embed.set_footer(text=f"From Server: {guild}")
                                await channel.send(embed=embed)

    e.start()
