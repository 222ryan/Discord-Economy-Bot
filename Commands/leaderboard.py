
import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency

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
            con = config['leaderboard_amount']
            embed = discord.Embed(title=f":trophy: {ctx.guild.name}'s Leaderboard | Top {con}", colour=config['leaderboard_embed_colour'])
            i = 1
            for x in rankings:
                try:
                    temp = ctx.guild.get_member(x["id"])
                    money = x["money"]
                    tempmoney = "{:,}".format(money)
                    embed.add_field(name=f"#{i}: {temp.name}",
                                    value=f"Balance: ```{currency}{tempmoney}```\n", inline=True)
                    i += 1
                    embed.set_thumbnail(url=ctx.guild.icon_url)
                except:
                    pass
                if i == config['leaderboard_amount'] + 1:
                    break
            await ctx.channel.send(embed=embed)
            return
        if leader_type.lower() == 'global':
            rankings = economy.find({"job_type": {"$exists": False}}).sort("money", -1)
            con = config['leaderboard_amount']
            embed = discord.Embed(title=f"🌎 Global Leaderboard | Top {con}", colour=config['leaderboard_embed_colour'])
            i = 1
            for x in rankings:
                try:
                    temp = ctx.guild.get_member(x["id"])
                    money = x["money"]
                    server = x['guildid']
                    guild = self.client.get_guild(server)
                    if str(guild) == 'None':
                        continue
                    tempmoney = "{:,}".format(money)
                    embed.add_field(name=f"#{i}: {temp.name} | {guild}",
                                    value=f"Balance: ```{currency}{tempmoney}```\n", inline=True)
                    i += 1
                    embed.set_thumbnail(url=ctx.guild.icon_url)
                except:
                    pass
                if i == config['leaderboard_amount'] + 1:
                    break
            await ctx.channel.send(embed=embed)



def setup(client):
    client.add_cog(leaderboard(client))