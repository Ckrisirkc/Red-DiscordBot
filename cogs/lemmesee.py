import discord
import aiohttp

class LemmeSee:
    def __init__(self, bot):
        self.bot = bot
    
    async def printToConsole(self, message):
        print("{0}|{1}|{2}: {3}".format(message.server, message.channel, message.author.name, message.content))

def setup(bot):
    n = LemmeSee(bot)
    bot.add_listener(n.printToConsole, "on_message")

