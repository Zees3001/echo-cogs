import discord
from discord.ext import commands

class Echotools:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vusers(self):
        """This does stuff!"""

        #Your code will go here
        await self.bot.say("I can do more stuff!")

def setup(bot):
    bot.add_cog(Echotools(bot))
