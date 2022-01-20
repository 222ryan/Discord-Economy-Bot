import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, embed_colour, error_embed_colour, success_embed_colour

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Sell(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sell(self, ctx, amount: int = None, *, item: str = None):
        # check if amount is none
        if amount is None or amount < 1:
            embed = discord.Embed(description=":x: You need to specify an amount!", color=error_embed_colour)
            await ctx.send(embed=embed)
            return
        # check if item is none
        if item is None:
            embed = discord.Embed(description=":x: You need to specify an item to sell!", color=error_embed_colour)
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

                # check if the item is not in the users inventory
                if item.title() not in economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}})["inventory"]:
                    embed = discord.Embed(description=":x: You don't have that item in your inventory!", color=error_embed_colour)
                    await ctx.send(embed=embed)
                    return

                else:
                    count = 0
                    # check if the user has more than amount in inventory_amount
                    for x in economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["inventory"]:
                        count += 1
                        if str(x) == item.title():
                            if economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})["inventory_amount"][count - 1] >= amount:
                                # add price to balance
                                economy.update_one(
                                    {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                    {"$inc": {"money": price * amount}})
                                # remove amount from inventory_amount
                                economy.update_one(
                                    {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                    {"$inc": {"inventory_amount." + str(count - 1): -amount}})
                                # if the amount is 0, remove the item from the inventory
                                if economy.find_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}})["inventory_amount"][
                                    count - 1] == 0:
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                        {"$pull": {"inventory": item.title()}})
                                    economy.update_one(
                                        {"guildid": ctx.guild.id, "id": ctx.author.id, "job_type": {"$exists": False}},
                                        {"$pull": {"inventory_amount": 0}})
                                # send success message
                                embed = discord.Embed(
                                    description=f":white_check_mark: You sold `x{amount} {item.title()}'s` for `{currency}{price * amount:,}`!",
                                    color=success_embed_colour)
                                await ctx.send(embed=embed)
                                return
                            else:
                                embed = discord.Embed(
                                    description=f":x: You don't have that many `{item.title()}'s` in your inventory!",
                                    color=error_embed_colour)
                                await ctx.send(embed=embed)
                                return





def setup(client):
    client.add_cog(Sell(client))