import discord
from discord.ext import commands
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Balance(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Balance Command
    @commands.command(aliases=['bal', 'money', 'profile'])
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        try:
            stats = economy.find_one({"guildid": ctx.guild.id, "id": member.id})
            if stats is None:
                embed = discord.Embed(title=":x: No Data Found!",
                                      colour=config['error_embed_colour'])
                await ctx.channel.send(embed=embed)
            else:

                embed = discord.Embed(title=f"{ctx.guild.name}'s Bank")
                embed.add_field(name="Money:", value=f"`{currency}{stats['money']}`")
                embed.add_field(name="Job:", value=f"`{stats['job']}`")
                embed.add_field(name="Daily Income:", value=f"`{currency}{stats['daily_income']}`")
                embed.set_footer(text=f"Viewing Info For: {member}")
                await ctx.send(embed=embed)

        except Exception as e:
            print(f"Balance generated an exception.\n\n{e}")


def setup(client):
    client.add_cog(Balance(client))