# import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from datetime import datetime
import os


class Away:
    """The Away cog"""
    def __init__(self, bot):
        self.bot = bot
        self.away_data = 'data/away/away.json'

    async def listener(self, message):
        tmp = {}
        for mention in message.mentions:
            tmp[mention] = True
        if message.author.id != self.bot.user.id:
            data = fileIO(self.away_data, 'load')
            for mention in tmp:
                if mention.mention in data:
                    if data[mention.mention]['MESSAGE'] is True:
                        msg = '{} is currently away.'.format(mention.name)
                    else:
                        msg = '{} is currently away and has set a personal message: {}'.format(mention.name, data[mention.mention]['MESSAGE'])
                    await self.bot.send_message(message.channel, msg)
        data2 = fileIO(self.away_data, 'load')
        if message.author.mention in data:
            msg = await self.bot.send_message(message.channel, 'Hey {}, welcome back. `(No longer set as away)`'.format(message.author.display_name))
            del data2[message.author.mention]
            fileIO(self.away_data, 'save', data2)
            await asyncio.sleep(15)
            try:
                await self.bot.delete_message(msg)
            except:
                print("Could not delete return message")
                
    @commands.command(pass_context=True, name="away")
    async def _away(self, context, *message: str):
        """Tell the bot you're away or back."""
        data = fileIO(self.away_data, 'load')
        author_mention = context.message.author.mention
        if author_mention in data:
            del data[author_mention]
            msg = 'You\'re now back.'
        else:
            data[context.message.author.mention] = {}
            if message:
                data[context.message.author.mention]['MESSAGE'] = " ".join(context.message.clean_content.split()[1:])
            else:
                data[context.message.author.mention]['MESSAGE'] = True
            msg = 'You\'re now set as away.'
        fileIO(self.away_data, 'save', data)
        await self.bot.say(msg)


def check_folder():
    if not os.path.exists('data/away'):
        print('Creating data/away folder...')
        os.makedirs('data/away')


def check_file():
    away = {}
    f = 'data/away/away.json'
    if not fileIO(f, 'check'):
        print('Creating default away.json...')
        fileIO(f, 'save', away)


def setup(bot):
    check_folder()
    check_file()
    n = Away(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)