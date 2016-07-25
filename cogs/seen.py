from discord.ext import commands
from .utils.dataIO import fileIO
from pytz import timezone
from datetime import datetime
import discord
import os

__version__ = '1.0.0' # gotta start somewhere

class Seen:
    '''Check when someone was last seen.'''
    def __init__(self, bot):
        self.bot = bot
        self.seen_path = 'data/seen/seen.json'

    async def listener(self, message):
        if not message.channel.is_private and self.bot.user.id != message.author.id:
            data = fileIO(self.seen_path, 'load')
            server = message.server
            author = message.author
            channel = message.channel
            content = message.content
            timestamp = message.timestamp #message.timestamp.astimezone(eastern) # TODO
            if server.id not in data:
                data[server.id] = {}
            if author.id not in data[server.id]:
                data[server.id][author.id] = {}
            if author.nick:
                data[server.id][author.id]['NAME'] = '{} ({})'.format(author.name, author.nick)
            else:
                data[server.id][author.id]['NAME'] = author.name
            data[server.id][author.id]['TIMESTAMP'] = str(timestamp)[:-7]
            data[server.id][author.id]['MESSAGE'] = content
            data[server.id][author.id]['CHANNEL'] = channel.mention
            fileIO(self.seen_path, 'save', data)
            
#    async def listener2(self, before, after):
#        if after.id != self.bot.user.id:
#            data = fileIO(self.seen_path, 'load')
#            server = after.server
#            if server.id not in data:
#                data[server.id] = {}
#            if after.id not in data[server.id]:
#                data[server.id][after.id] = {}
#            if after.nick:
#                data[server.id][after.id]['NAME'] = '{} ({})'.format(after.name, after.nick)
#            else:
#                data[server.id][after.id]['NAME'] = after.name
#            if after.status == discord.Status.offline:
#                data[server.id][after.id]['LAST_ONLINE'] = datetime.now()
#            data[server.id][after.id]


    @commands.command(pass_context=True, no_pm=True, name='seen', aliases=['s'])
    async def _seen(self, context, username: discord.Member):
        '''seen <@username>'''
        data = fileIO(self.seen_path, 'load')
        server = context.message.server
        author = username
        if server.id in data:
            if author.id in data[server.id]:
                timestamp = data[server.id][author.id]['TIMESTAMP']
                last_msg = data[server.id][author.id]['MESSAGE']
                user_name = data[server.id][author.id]['NAME']
                channel_name = data[server.id][author.id]['CHANNEL']
                message = '{0} was last seen on `{1} UTC` in {2}, saying: {3}'.format(user_name, timestamp, channel_name, last_msg)
            elif author.mention in data[server.id]:
                # legacy
                timestamp = data[server.id][author.mention]['TIMESTAMP']
                last_msg = data[server.id][author.mention]['MESSAGE']
                user_name = data[server.id][author.mention]['NAME']
                channel_name = data[server.id][author.mention]['CHANNEL']
                message = '{0} was last seen on `{1} UTC` in {2}, saying: {3}'.format(user_name, timestamp, channel_name, last_msg)

            else:
                message = 'I have not seen {0} yet.'.format(author.name)
        else:
            message = 'I haven\'t seen anyone in this server yet!'
        await self.bot.say('{0}'.format(message))


def check_folder():
    if not os.path.exists('data/seen'):
        print('Creating data/seen folder...')
        os.makedirs('data/seen')


def check_file():
    data = {}
    f = 'data/seen/seen.json'
    if not fileIO(f, 'check'):
        print('Creating default seen.json...')
        fileIO(f, 'save', data)



def setup(bot):
    check_folder()
    check_file()
    n = Seen(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)
