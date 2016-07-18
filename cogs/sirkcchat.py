import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
from collections import deque
from cogs.utils.chat_formatting import escape_mass_mentions
import os
import logging
import asyncio


class SirkcChat:
    """Random shit relating to chat."""
    
    def __init__(self, bot):
        self.bot = bot
        self.chanList = {}
        self.recordList = {}
        self.defaultMon = False
    
    async def _delAfterTime(self, msgs, time=20):
        await asyncio.sleep(time)
        for msg in msgs:
            try:
                await self.bot.delete_message(msg)
            except discord.Forbidden:
                print("Cannot delete message, Forbidden")
            except discord.NotFound:
                print("Cannot delete message, Not Found")
    
    def _monitoringChannel(self, chan_id):
        if chan_id not in self.chanList:
            self.chanList[chan_id] = self.defaultMon
        return self.chanList[chan_id]
    
    @commands.group(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def sirkcchat(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return
    
    @sirkcchat.command(name="limitspam", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def limitSpam(self, ctx):
        chan = ctx.message.channel.id
        if (self._monitoringChannel(chan)):
            self.chanList[chan] = False
            msg = await self.bot.say("Alright, I'll stop monitoring this channel.")
        else:
            self.chanList[chan] = True
            msg = await self.bot.say("Okay, started monitoring this channel.")
        await self._delAfterTime([msg, ctx.message], time=7)
            

    async def spamChecker(self, message):
        if not message.channel.id in self.recordList:
            self.recordList[message.channel.id] = {}
        if not message.author.id in self.recordList[message.channel.id]:
            self.recordList[message.channel.id][message.author.id] = []
        #mcontent = message.content
        if len(self.recordlist[message.channel.id][message.author.id]) >= 10:
            del self.recordlist[message.channel.id][message.author.id][0]
        self.recordlist[message.channel.id][message.author.id].append(message)
        
        if not (self._monitoringChannel(message.channel.id)):
            return
        tempDict = {}
        tempArray = []
        for msg in self.recordlist[message.channel.id][message.author.id]:
            if msg.content.lower() not in tempDict:
                tempDict[msg.content.lower()] = 1
                tempArray.append(msg.content.lower())
            else:
                tempDict[msg.content.lower()] = tempDict[msg.content.lower()] + 1
        for ele in tempArray:
            if tempDict[ele] >= 5:
                logger.info("User {} is spamming the channel {} on server {}".format(message.author.display_name, message.channel.name, message.server.name))
                for rem in self.recordList[message.channel.id][message.author.id]:
                    if ele in rem.content.lower():
                        await self._delAfterTime([rem], time=0)

def check_folders():
    if not os.path.exists("data/sirkcchat"):
        print("Creating data/sirkcchat folder...")
        os.makedirs("data/sirkcchat")

def check_files():

    #f = "data/sirkcchat/responses.json"
    #if not fileIO(f, "check"):
    #    print("Creating sirkctemp responses.json...")
    #    fileIO(f, "save", {})

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("sirkcchat")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/sirkcchat/sirkcchat.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = SirkcChat(bot)
    bot.add_listener(n.spamChecker, "on_message")
    bot.add_cog(n)