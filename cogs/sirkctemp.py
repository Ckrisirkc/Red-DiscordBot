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
from copy import deepcopy


class Sirkctemp:
    """Random shit."""
    
    def __init__(self, bot):
        self.bot = bot
        self.responses = dataIO.load_json("data/sirkctemp/responses.json")
        self.forcedppl = {}
    
    async def _delAfterTime(self, msgs, time=20):
        await asyncio.sleep(time)
        for msg in msgs:
            try:
                await self.bot.delete_message(msg)
            except discord.Forbidden:
                print("Cannot delete message, Forbidden")
            except discord.NotFound:
                print("Cannot delete message, Not Found")

    @commands.command(name="forcechan", no_pm=True, pass_context=True)
    @checks.admin_or_permissions(move_members=True)
    async def forceChannel(self, ctx, user : discord.Member, chan : discord.Channel):
        """Forces a user into a voice channel"""
        if not chan.type == discord.ChannelType.voice:
            msg = await self.bot.say("Channel must be a voice channel")
            await self._delAfterTime([ctx.message, msg])
            return
        if user.id == settings.owner:
            if not ctx.message.author.id == settings.owner:
                msg = await self.bot.say("I won't ever force my owner to do anything!")
                await self._delAfterTime([ctx.message, msg])
                return
        server = ctx.message.server
        if server.id not in self.forcedppl:
            self.forcedppl[server.id] = {}
        self.forcedppl[server.id][user.id] = chan
        msg = await self.bot.say("Will do!")
        await self.checkforces(None, user)
        await self._delAfterTime([ctx.message, msg])
        
    @commands.command(name="unforcechan", no_pm=True, pass_context=True)
    @checks.admin_or_permissions(move_members=True)
    async def unforceChannel(self, ctx, user : discord.Member):
        """unForces a user who is forced into a voice channel"""
        if not self._isForced(user):
            msg = await self.bot.say("User not chanForced")
            await self._delAfterTime([ctx.message, msg])
            return
        server = ctx.message.server
        del self.forcedppl[server.id][user.id]
        msg = await self.bot.say("Got it!")
        await self._delAfterTime([ctx.message, msg])
    
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
            try:
                await self.bot.move_member(after, toChan)
            except:
                print("Cannot move {} to {}".format(after.display_name, toChan.name))
                

    @commands.command(name="massmove", no_pm=True, pass_context=True)
    @checks.admin_or_permissions(move_members=True)
    async def massMove(self, ctx, frm : discord.Channel, to : discord.Channel):
        """Moves everyone in one voice channel to another voice channel"""
        if not (frm.type == discord.ChannelType.voice and to.type == discord.ChannelType.voice):
            msg = await self.bot.say("Channels must be voice channels")
            await self._delAfterTime([ctx.message, msg])
            return
        in_ch = len(frm.voice_members) + len(to.voice_members)
        to_limit = to.user_limit
        if (in_ch > to_limit and to_limit != 0):
            msg = await self.bot.say("The channel you want to move to does not have enough space in it.")
            await self._delAfterTime([ctx.message, msg])
            return
            
        if not ctx.message.author in frm.voice_members:
            if not ctx.message.author.id == settings.owner:
                msg = await self.bot.say("You must be in the channel you want to move from to use this command")
                await self._delAfterTime([ctx.message, msg])
                return
        for member in frm.voice_members:
            try:
                await self.bot.move_member(member, to)
            except:
                print("Cannot move {} to {}".format(after.display_name, toChan.name))
    
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def quickcmd(self, ctx, *, command):
        """Runs the [command] and instantly deletes the message DON'T ADD A PREFIX
        """
        new_msg = deepcopy(ctx.message)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            print("error deleting insta msg")
        
        new_msg.content = self.bot.command_prefix[0] + command
        await self.bot.process_commands(new_msg)
        await self.bot.purge_from(ctx.channel, after=ctx.message, check=lambda x:x.author == self.bot.user or x.author == ctx.author)
      

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