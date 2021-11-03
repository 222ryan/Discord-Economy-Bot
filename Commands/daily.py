import datetime

import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from ruamel.yaml import YAML

from Systems.Economy import economy
from main import currency, success_embed_colour, error_embed_colour

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class Daily(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Daily Command
    @commands.command()
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily(self, ctx):
        stats = economy.find_one({"guildid": ctx.guild.id, "id": ctx.author.id})
        money = stats['money']
        economy.update_one({"guildid": ctx.guild.id, "id": ctx.author.id},
                           {"$set": {"money": money + config['daily']}})
        embed = discord.Embed(title="✅ Daily Claimed",
                              description=f"{ctx.author.mention}, you have earned `{currency}{config['daily']}`!", colour=success_embed_colour)
        embed.add_field(name="Balance", value=f"`${money + config['daily']}`")
        embed.set_footer(text="Come back tomorrow to redeem again!")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):

            seconds = int(error.retry_after)
            time_remaining = str(datetime.timedelta(seconds=seconds))

            embed = discord.Embed(description=f":x: {ctx.author.mention}, Slow down!", colour=error_embed_colour)
            embed.set_footer(text=f"Try again in: {time_remaining}")
            await ctx.send(embed=embed)
            return
        raise error


def setup(client):
    client.add_cog(Daily(client))
