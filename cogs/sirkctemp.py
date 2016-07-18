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


class Sirkctemp:
    """Random shit."""
    
    def __init__(self, bot):
        self.bot = bot
        self.responses = dataIO.load_json("data/sirkctemp/responses.json")
        self.forcedppl = {}

    @commands.command(name="forcechan", no_pm=True, pass_context=True)
    @checks.admin_or_permissions(move_members=True)
    async def forceChannel(self, ctx, user : discord.Member, chan : discord.Channel):
        """Forces a user into a voice channel"""
        if not chan.type == discord.ChannelType.voice:
            await self.bot.say("Channel must be a voice channel")
            return
        if user.id == settings.owner:
            await self.bot.say("I won't ever force my master to do anything!")
            return
        server = ctx.message.server
        if server.id not in self.forcedppl:
            self.forcedppl[server.id] = {}
        self.forcedppl[server.id][user.id] = chan
        await self.bot.say("Will do!")
        await self.checkforces(None, user)
        
    @commands.command(name="unforcechan", no_pm=True, pass_context=True)
    @checks.admin_or_permissions(move_members=True)
    async def unforceChannel(self, ctx, user : discord.Member):
        """unForces a user who is forced into a voice channel"""
        if not self._isForced(user):
            await self.bot.say("User not chanForced")
            return
        server = ctx.message.server
        del self.forcedppl[server.id][user.id]
        await self.bot.say("Got it!")
    
    def _isForced(self, member):
        server = member.server
        if server.id in self.forcedppl:
            if member.id in self.forcedppl[server.id]:
                return self.forcedppl[server.id][member.id]
        return None
        
    async def checkforces(self, before, after):
        if after.voice_channel is None:
            return
        toChan = self._isForced(after)
        if toChan is None:
            return
        if not after.voice_channel == toChan:
            await self.bot.move_member(after, toChan)
            
def check_folders():
    if not os.path.exists("data/sirkctemp"):
        print("Creating data/sirkctemp folder...")
        os.makedirs("data/sirkctemp")

def check_files():

    f = "data/sirkctemp/responses.json"
    if not fileIO(f, "check"):
        print("Creating sirkctemp responses.json...")
        fileIO(f, "save", {})

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("sirkctemp")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/sirkctemp/sirkctemp.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = Sirkctemp(bot)
    bot.add_listener(n.checkforces, "on_voice_state_update")
    bot.add_cog(n)