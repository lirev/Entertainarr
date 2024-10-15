import discord
from discord.ext import commands
import admin_commands
import ext_commands
import movies
import shows
import ctxcore
import configparser
import asyncio
import os

# Load the configuration file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)

#discord intents, manages bot permissions
intents = discord.Intents.default() 
intents.typing = True
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents) 
last_movie = None
user = None
token = config['API']['TOKEN']

#setup the commands
admin_commands.setup(bot)
ext_commands.setup(bot)
movies.setup(bot)
shows.setup(bot)
    
# Event for processing commands
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
  
#help command            
@bot.command(aliases=['h','H','Help'])
async def bothelp(ctx):
        await ctx.send("Add any movie or show by sending a command!")
        await ctx.send("To add a movie use !m or !movie, if result is not as expected, iterate through search with a number I.E. \"!m thirteen ghosts 2\", this will use the second option returned and so on. bot will direct message when movie is available on plex.")
        await ctx.send("to add a show use !s or !show. iteration needs to be added. bot will direct message when show is available on plex.") 

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Ready to serve!')

async def main():
    async with bot:
        await bot.start(token)
asyncio.run(main())
