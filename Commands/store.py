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


class Store(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()

    async def store(self, ctx):
        # create an array of items that include the item name, price, and description and then paginate them into an embed
        embed = discord.Embed(
            title=f"🏪 STORE | {ctx.guild}",
            colour=embed_colour,

        )
        embed.set_footer(text=f"!buy <amount> <item>")

        items = config['items']
        price = config['prices']
        description = config['description']

        # use items, price and description to create a list of items and then paginate them with reactions to switch pages

        pagination = list(zip(items, price, description))
        pages = [pagination[i:i + 10] for i in range(0, len(pagination), 10)]
        page = 0
        for i in pages:
            embed.clear_fields()
            for item, price, description in i:
                embed.add_field(name=f"{item}", value=f"Price: `{currency}{price:,}`\n{description}", inline=False)
            embed.set_footer(text=f"Page {page + 1}/{len(pages)} | !buy <amount> <item>")
            message = await ctx.send(embed=embed)
            page += 1
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("❌")

            while True:
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️", "❌"] and reaction.message.id == message.id

                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

                    if str(reaction.emoji) == "⬅️":
                        if page == 1:
                            pass
                        else:
                            page -= 1
                            embed.clear_fields()
                            for item, price, description in pages[page - 1]:
                                embed.add_field(name=f"{item}", value=f"Price: `{currency}{price:,}`\n{description}", inline=False)
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
                            for item, price, description in pages[page - 1]:
                                embed.add_field(name=f"{item}", value=f"Price: `{currency}{price:,}`\n{description}", inline=False)
                            embed.set_footer(text=f"Page {page}/{len(pages)} | !buy <amount> <item>")
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
    client.add_cog(Store(client))
