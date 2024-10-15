import discord
from discord.ext import commands
import admin_commands
import ext_commands
import movies
from movies import *
from shows import *
import ctxcore
import asyncio

#discord intents, manages bot "permissions
intents = discord.Intents.default()  # or .all() if you ticked all, that is easier
intents.typing = True
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)  # intialization of bot and "Import" the intents
last_movie = None
user = None
token = config['API']['TOKEN']

# Register the commands
admin_commands.setup(bot)
ext_commands.setup(bot)
movies.setup(bot)
shows.setup(bot)
    
# Event for processing commands
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Process commands
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
        #bot.loop.create_task(recently())
        #recently.start()
        await bot.start(token)
asyncio.run(main())
