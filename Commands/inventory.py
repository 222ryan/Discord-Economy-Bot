import asyncio
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, success_embed_colour, error_embed_colour, embed_colour

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Inventory(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def inventory(self, ctx):
        user = economy.find_one({'id': ctx.author.id, 'guildid': ctx.guild.id, "job_type": {"$exists": False}})
        embed = discord.Embed(
            title=f"🎒 {ctx.author}'s Inventory",
            colour=embed_colour,

        )

        items = user['inventory']
        amount = user['inventory_amount']

        if len(items) < 1:
            embed.add_field(name="You have no items in your inventory!", value=f"`Use {config['Prefix']}store to access the store!`")
            await ctx.send(embed=embed)
            return
        pagination = list(zip(items, amount))
        pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
        page = 0
        num = 0
        items_list = []
        amount_list = []
        for i in pages:
            embed.clear_fields()
            # check if items is none
            for items, amount in i:
                num += 1
                embed.add_field(name=f"#{num}: {items}", value=f"You own `{amount:,}`", inline=True)

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
                            for items, amount in pages[page - 1]:
                                num -= 1
                                items_list.append(items)
                                amount_list.append(amount)
                            for x in range(0, 10):
                                embed.add_field(name=f"#{x + 1 + num - len(items_list)}: {items_list[x]}",
                                                value=f"You own `{amount:,}`", inline=True)
                            items_list.clear()
                            amount_list.clear()
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
                            for items, amount in pages[page - 1]:
                                num += 1
                                items_list.append(items)
                                amount_list.append(amount)
                                embed.add_field(name=f"#{num}: {items}", value=f"You own `{amount:,}`",
                                                inline=True)
                            if len(items) != 10:
                                get_ten = 10 - len(items)
                                num += get_ten
                            items_list.clear()
                            amount_list.clear()
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
    client.add_cog(Inventory(client))
