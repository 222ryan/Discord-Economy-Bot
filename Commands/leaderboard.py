import asyncio

import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, success_embed_colour, leader_embed

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Leaderboard Command
    @commands.command(aliases=config['leaderboard_alias'])
    @commands.guild_only()
    async def leaderboard(self, ctx, leader_type=None):
        if leader_type is None:
            rankings = economy.find({"guildid": ctx.guild.id, "money": {"$exists": True}, "job_type": {"$exists": False}}).sort("money", -1)
            users = []
            money = []
            for x in rankings:
                users.append(x['name'])
                money.append(x['money'])
            embed = discord.Embed(
                title=f":trophy: {ctx.guild}'s Leaderboard",
                colour=leader_embed,

            )
            embed.set_footer(text=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            pagination = list(zip(users, money))
            pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
            page = 0
            num = 0
            user_list = []
            balance_list = []
            for i in pages:
                embed.clear_fields()
                for users, money in i:
                    num += 1
                    embed.add_field(name=f"#{num}: {users}", value=f"```{currency}{money:,}```", inline=True)
                embed.set_footer(text=f"Page {page + 1}/{len(pages)}")
                message = await ctx.send(embed=embed)
                page += 1
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")
                await message.add_reaction("❌")

                while True:
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️",
                                                                              "❌"] and reaction.message.id == message.id

                    try:
                        reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "⬅️":
                            if page == 1:
                                pass
                            else:
                                page -= 1
                                embed.clear_fields()
                                for users, money in pages[page - 1]:
                                    num -= 1
                                    user_list.append(users)
                                    balance_list.append(money)
                                for x in range(0, 10):
                                    embed.add_field(name=f"#{x + 1 + num - len(user_list)}: {user_list[x]}", value=f"```{currency}{balance_list[x]:,}```", inline=True)
                                user_list.clear()
                                balance_list.clear()
                                embed.set_footer(text=f"Page {page}/{len(pages)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction("⬅️", user)
                                await message.remove_reaction("➡️", user)
                                await message.remove_reaction("❌", user)
                        elif str(reaction.emoji) == "➡️":
                            if page == len(pages):
                                pass
                            else:
                                page += 1
                                embed.clear_fields()
                                new_num = num
                                for users, money in pages[page - 1]:
                                    num += 1
                                    user_list.append(users)
                                    balance_list.append(money)
                                    embed.add_field(name=f"#{num}: {users}", value=f"```{currency}{money:,}```",
                                                    inline=True)
                                if len(user_list) != 10:
                                    get_ten = 10 - len(user_list)
                                    num += get_ten
                                user_list.clear()
                                balance_list.clear()
                                embed.set_footer(text=f"Page {page}/{len(pages)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction("⬅️", user)
                                await message.remove_reaction("➡️", user)
                                await message.remove_reaction("❌", user)
                        elif str(reaction.emoji) == "❌":
                            await message.delete()
                            return
                    except asyncio.TimeoutError:
                        await message.delete()
                        return

        elif leader_type.lower() == "global":
            rankings = economy.find(
                {"money": {"$exists": True}, "job_type": {"$exists": False}}).sort("money", -1)
            users = []
            money = []
            guild = []
            for x in rankings:
                users.append(x['name'])
                money.append(x['money'])
                guild.append(x['guildid'])
            embed = discord.Embed(
                title=f"🌎 Global Leaderboard",
                colour=leader_embed,

            )
            embed.set_footer(text=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            pagination = list(zip(users, money, guild))
            pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
            page = 0
            num = 0
            user_list = []
            balance_list = []
            guild_list = []
            for i in pages:
                embed.clear_fields()
                for users, money, guild in i:
                    num += 1
                    embed.add_field(name=f"#{num}: {users}\n`{self.client.get_guild(guild)}`", value=f"```{currency}{money:,}```", inline=True)
                embed.set_footer(text=f"Page {page + 1}/{len(pages)}")
                message = await ctx.send(embed=embed)
                page += 1
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")
                await message.add_reaction("❌")

                while True:
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️",
                                                                              "❌"] and reaction.message.id == message.id

                    try:
                        reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "⬅️":
                            if page == 1:
                                pass
                            else:
                                page -= 1
                                embed.clear_fields()
                                for users, money, guild in pages[page - 1]:
                                    num -= 1
                                    user_list.append(users)
                                    balance_list.append(money)
                                    guild_list.append(guild)
                                for x in range(0, 10):
                                    embed.add_field(name=f"#{x + 1 + num - len(user_list)}: {user_list[x]}\n`{self.client.get_guild(guild_list[x])}`",
                                                    value=f"```{currency}{balance_list[x]:,}```", inline=True)
                                user_list.clear()
                                balance_list.clear()
                                guild_list.clear()
                                embed.set_footer(text=f"Page {page}/{len(pages)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction("⬅️", user)
                                await message.remove_reaction("➡️", user)
                                await message.remove_reaction("❌", user)
                        elif str(reaction.emoji) == "➡️":
                            if page == len(pages):
                                pass
                            else:
                                page += 1
                                embed.clear_fields()
                                new_num = num
                                for users, money, guild in pages[page - 1]:
                                    num += 1
                                    user_list.append(users)
                                    balance_list.append(money)
                                    guild_list.append(guild)
                                    embed.add_field(name=f"#{num}: {users}\n`{self.client.get_guild(guild)}`", value=f"```{currency}{money:,}```",
                                                    inline=True)
                                if len(user_list) != 10:
                                    get_ten = 10 - len(user_list)
                                    num += get_ten
                                user_list.clear()
                                balance_list.clear()
                                guild_list.clear()
                                embed.set_footer(text=f"Page {page}/{len(pages)}")
                                await message.edit(embed=embed)
                                await message.remove_reaction("⬅️", user)
                                await message.remove_reaction("➡️", user)
                                await message.remove_reaction("❌", user)
                        elif str(reaction.emoji) == "❌":
                            await message.delete()
                            return
                    except asyncio.TimeoutError:
                        await message.delete()
                        return



def setup(client):
    client.add_cog(leaderboard(client))