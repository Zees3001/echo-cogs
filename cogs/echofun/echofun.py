import discord
from discord.ext import commands
from random import randint
import aiohttp
import random

class Echofun:
    """echo fun commands."""

    def __init__(self, bot):
        self.bot = bot
        #Reserved for further ...

    """Commands section"""

    @commands.command(no_pm=True)
    async def sr(self, *text):
        """sr [keyword] - Retrieves a random picture from subreddit"""
        imgurclient = ImgurClient("ad8952f4d3e875e", "7438169dd1b096d0dca330e826aeb120fbec6bcc")
        if text[0] != ():
            randpage = randint(0, 9) #randomize page 0-9
            items = imgurclient.gallery_search(" ".join(text[0:len(text)]), advanced=None, sort='time', window='all', page=randpage)
            rand = randint(0, len(items)) #randomize result
            if len(items) < 1:
                await self.bot.say("No result for: {}".format(text[0]))
            else:
                await self.bot.say(items[rand].link)
        
        elif text[0] == ():
            await self.bot.say("Type help sr for details.")

class ModuleNotFound(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message

def setup(bot):
    global ImgurClient
    try:
        from imgurpython import ImgurClient
    except:
        raise ModuleNotFound("imgurpython is not installed. Do 'pip3 install imgurpython' to use this cog.")
    bot.add_cog(Echofun(bot))