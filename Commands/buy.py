import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, embed_colour, error_embed_colour

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Buy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def buy(self, ctx, amount: int = None, *, item: str = None):
        # check if amount is none
        if amount is None or amount < 1:
            embed = discord.Embed(description=":x: You need to specify an amount!", color=error_embed_colour)
            await ctx.send(embed=embed)
            return
        # check if item is none
        if item is None:
            embed = discord.Embed(description=":x: You need to specify an item to buy!", color=error_embed_colour)
            await ctx.send(embed=embed)
            return
        # check if item is in the config
        if item.title() not in config["items"]:
            embed = discord.Embed(description=":x: That item doesn't exist!", color=error_embed_colour)
            await ctx.send(embed=embed)
            return

        count = 0
        for i in config["items"]:
            count += 1
            if str(i).lower() == item.lower():
                item_price = config["prices"]
                price = item_price[count - 1]

                # check if the user has enough money
                if economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["money"] < price:
                    embed = discord.Embed(description=":x: You don't have enough money to buy that!", color=error_embed_colour)
                    await ctx.send(embed=embed)
                    return
                else:
                    count = 0
                    # check if item is in the users inventory, and if it is , add the amount to the amount
                    for x in economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["inventory"]:
                        count += 1
                        if str(x) == item.title():
                            # find the item in the inventory and add the amount
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                               {"$inc": {f"inventory_amount.{count - 1}": + amount}})
                            # remove the money from the user
                            economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                               {"$inc": {"money": -price * amount}})
                            embed = discord.Embed(
                                description=f":white_check_mark: You bought `x{amount} {item.title()}'s` for `{currency}{price}`!",
                                color=embed_colour)
                            await ctx.send(embed=embed)
                            return

                    # if the item is not in the users inventory, add the item and the amount
                    economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                       {"$push": {f"inventory": str(item).title()},
                                        "$inc": {f"inventory_amount.{count}": + amount}})









                    embed = discord.Embed(description=f":white_check_mark: You bought `x{amount} {item}'s` for `{currency}{price}`!", color=embed_colour)
                    await ctx.send(embed=embed)
                    return




def setup(client):
    client.add_cog(Buy(client))