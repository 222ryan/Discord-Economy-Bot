import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Pay(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Pay Command
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def pay(self, ctx, member: discord.Member = None, amount=None, *, message=None):
        if member is None:
            member = ctx.author
        if message is None:
            message = f"There was no message attached to this payment!"
        try:
            author = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
            stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id})
            if stats is None:
                embed = discord.Embed(description=":x: Something went wrong!",
                                      colour=config['error_embed_colour'])
                await ctx.channel.send(embed=embed)
            else:
                if member == ctx.author or ctx.author.bot:
                    embed = discord.Embed(description=":x: You cannot pay yourself!")
                    await ctx.send(embed=embed)
                    return
                if amount is None:
                    embed = discord.Embed(description=":x: You need to specify how much you would like to send!")
                    await ctx.send(embed=embed)
                    return
                else:
                    author_money = author['money']
                    receiver = stats['money']
                    if int(author_money) < int(amount):
                        embed = discord.Embed(description=":x: You have insufficient funds!")
                        embed.add_field(name="Balance:", value=f"`{currency}{author_money}`")
                        await ctx.send(embed=embed)
                    else:
                        economy.update_one({"guildid": ctx.guild.id, "id": member.id},
                                           {"$set": {"money": receiver + int(amount)}})
                        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                                           {"$set": {"money": author_money - int(amount)}})
                        embed = discord.Embed(title="✅ Payment Successful!", description=f"You sent `{currency}{amount}` to {member.mention}!")
                        embed.add_field(name="Balance", value=f"`{currency}{int(author_money) - int(amount)}`")
                        await ctx.send(embed=embed)

                        channel = await member.create_dm()
                        embed = discord.Embed(title=f"Payment From {ctx.author}", description=f"You have received `{currency}{amount}` from {ctx.author.mention}!")
                        embed.add_field(name="Balance:", value=f"`{currency}{int(receiver) + int(amount)}`")
                        embed.add_field(name="Message:", value=f"`{message}`", inline=False)
                        await channel.send(embed=embed)




        except Exception as e:
            print(f"Pay generated an exception.\n\n{e}")
            embed = discord.Embed(description=":x: You need to enter a valid number to send a payment!")
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Pay(client))