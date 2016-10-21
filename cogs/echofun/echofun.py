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
        imgurclient = ImgurClient("1fd3ef04daf8cab", "f963e574e8e3c17993c933af4f0522e1dc01e230")
        if text[0] != ():
            rand = randint(0, 29) #60 results per generated page
            randpage = randint(0, 9) #random page 0
            items = imgurclient.gallery_search(" ".join(text[0:len(text)]), advanced=None, sort='time', window='all', page=randpage)
            if len(items) < 1:
                await self.bot.say("Your search terms gave no results.")
            else:
                await self.bot.say(len(items)) #items[rand].link)
        
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