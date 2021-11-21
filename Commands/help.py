import discord
from discord.ext import commands

from main import config


class help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["h", "eh"])
    @commands.guild_only()
    async def help(self, ctx, helptype=None):
        if config['help_command'] is True:
            prefix = config['Prefix']
            top = config['leaderboard_amount']
            embed = discord.Embed(title=f"{self.client.user.name} Command List")
            if helptype is None:
                embed.add_field(name=f":smile: Fun",
                                value=f"`{prefix}help fun`\n[Hover for info](https://www. 'Fun Commands such as begging, daily, balance and more!')")
                embed.add_field(name=f":game_die: Gambling",
                                value=f"`{prefix}help gambling`\n[Hover for info](https://www. 'Gamble commands to "
                                      f"bet your money')")
                embed.add_field(name=f"💼 Jobs",
                                value=f"`{prefix}help jobs`\n[Hover for info](https://www. 'Shows information regarding Jobs "
                                      f"bet your money')")
                embed.add_field(name=f"🛍️ Shopping",
                                value=f"`{prefix}help shopping`\n[Hover for info](https://www. 'Shows information regarding shopping')")
                embed.set_footer(text="If you're on mobile, the hover button will not work")
                await ctx.send(embed=embed)
            elif helptype.lower() == "fun":
                embed = discord.Embed(title=f":smile: Fun Commands",
                                      description="```balance, beg, daily, leaderboard, pay, rob```")
                embed.add_field(name="Examples",
                                value=f"```🪙 balance [user] - Displays the users current Balance, Job and Daily Income\n"
                                      f"📊 leaderboard [global] - Displays top {top} users in the Server or Global"
                                      f" Rankings\n"
                                      f"🧎‍♂️  beg - Beg for money and receive potential a positive or a negative result\n"
                                      f"☀️ daily - Receive your Daily Reward of {config['daily']}\n"
                                      f"💸 pay <@user> <amount> [message] - Pay another user an amount of money"
                                      f"\n💰 rob <@user> - Attempt to rob another user```")
                await ctx.send(embed=embed)
            elif helptype.lower() == "gambling":
                embed = discord.Embed(title=f":game_die: Gambling Commands",
                                      description="```bet, highlow, slots```")
                embed.add_field(name="Examples",
                                value=f"```🎲 - bet <amount> <red|black> - Bet on a certain colour, and if your guess "
                                      f"is correct, you will earn x2 the amount, else you will lose your money\n"
                                      f"🔼 - highlow - Guess if the the number is Higher or Lower than the number shown\n"
                                      f"🎰 - slots <amount> - Spin the slots machine to earn high rewards!```")

                await ctx.send(embed=embed)
            elif helptype.lower() == "jobs":
                embed = discord.Embed(title=f"💼 Job Commands",
                                      description="```job, quitjob```")
                embed.add_field(name="Examples",
                                value=f"```💼 job [user] - Views info about a users job. If the user does not have a job, it will display available jobs\n"
                                      f"👋 quitjob - Quits your current job"
                                      f"🏢 apply <jobName> - Apply for a job```")

                await ctx.send(embed=embed)
            elif helptype.lower() == "shopping":
                embed = discord.Embed(title=f"🛍️ Shopping Commands",
                                      description="```store, buy, sell, inventory```")
                embed.add_field(name="Examples",
                                value=f"```🛍️ store - Displays the store\n"
                                      f"💸 buy <amount> <item> - Buy an item from the store\n"
                                      f"💰 sell <amount> <item> - Sell an item to the store\n"
                                      f"🎒 inventory - Displays your inventory```")

                await ctx.send(embed=embed)

def setup(client):
    client.add_cog(help(client))
