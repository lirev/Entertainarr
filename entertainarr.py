import discord
from discord.ext import commands, tasks
from plexapi.myplex import MyPlexAccount
from arrapi import RadarrAPI, SonarrAPI
from pyarr import SonarrAPI as sapi
from tmdbv3api import TMDb, Movie as M
import os
import ctxcore
import asyncio
import json
import configparser

#sets absolute path of python script and reads the config.ini file for keys
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)

#discord
TOKEN = config['API']['TOKEN']

#radarr
host_url = config['API']['host_url']
api_key = config['API']['api_key']
radarr = RadarrAPI(host_url, api_key)

#sonarr
sapi_key = config['API']['sapi_key']
shost_url = config['API']['shost_url']
sonarr = SonarrAPI(shost_url, sapi_key)
sonarr2 = sapi(shost_url, sapi_key)

#plex
plexUser = config['API']['plexUser']
plexPass = config['API']['plexPass']
plexServer = config['API']['plexServer']
account = MyPlexAccount(plexUser, plexPass)
plex = account.resource(plexServer).connect() 

quality_profile = config['API']['quality_profile']
language = config['API']['language']

#tdmb
m = M()
tmdb=TMDb()
tmdb_url ='https://image.tmdb.org/t/p/w500/'
tmdb_api = config['API']['tmdb_api']
tmdb.api_key=tmdb_api
tmdb.language = 'en'
channel_id = config['API']['channel_id']

#discord intents, manages bot "permissions"
intents = discord.Intents.default()  # or .all() if you ticked all, that is easier
intents.typing = True
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)  # intialization of bot and "Import" the intents
last_movie = None
user = None

# get recently added movies
@tasks.loop(minutes=5.0)
async def recently():
    global last_movie
    global user
    # get the list of recently added movies
    recent_movies = plex.library.recentlyAdded()
    # get the first movie in the list
    new_movie = recent_movies[0]
    channel1 = bot.get_channel(channel_id)
    # check if the first movie is different from the last movie
    if new_movie != last_movie:
        last_movie = new_movie
        movie_string = str(new_movie)
        movie_title = movie_string.split(':')[2]
        await bot.wait_until_ready()
        #send title to discord channel
        if movie_title == 0:
            await channel1.send(f"{movie_title}is now available on plex.")
        #send direct message to user who requested the title
        if user != None:
            await user.send(f"{new_movie} is now available on Plex.")
            user = None
    await asyncio.sleep(60)
    
    
    
#basic fucntion for calling bot with !m, !M, !Movie
@bot.command(aliases=['m','M','Movie'])
async def movies(ctx,*, title):
    #assign user to a variable
    global user
    user = ctx.author
    #checks if the user entered a result number
    # Split input string into title and increment number
    parts = title.split(':')
    title = parts[0].strip()
    increment_str = parts[1].strip() if len(parts) > 1 else '1'
    result_number = int(increment_str)
    if result_number > 10 or result_number < 1:
        await ctx.send("Invalid result number, please enter a number within the range of search results.")        
    await ctx.send(f"Searching Radarr for {title} with increment {result_number}")
    search = m.search(title)
    i = 1
    for res in search:
        if i == result_number:
            list = res.id
            poster = tmdb_url+res.poster_path
            break
        i += 1
    movie = radarr.get_movie(tmdb_id=list)
    await ctx.send(poster)
    movie_path = config['API']['movie_path']
    await ctx.send("Is this correct? Just type yes or no.")
    def check(m):
        return m.content.lower() in ("yes", "no") and m.channel == ctx.channel
    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Timed out, please try again.")
    else:
        if msg.content.lower() == "yes":
            try:
                radarr.add_movie(tmdb_id=list, quality_profile=quality_profile, root_folder=movie_path)
                await ctx.send(f"Added movie to radarr library: {movie}")
            except:
                await ctx.send(f"Failed to add {movie}. Maybe its already in the radarr library? \nIf no results, try changing your search term.")
        else:
            await ctx.send("Cancelled.")
      
   
#start of tv shows
#this ia a more compressed version of the movie fucntions. 
@bot.command(aliases=['s','S','Shows'])
async def shows(ctx,*, title):
    await ctx.send(f"Searching Sonarr for {title}.")
    series = sonarr2.lookup_series(title)
    print(title)
    for res in series:
        id =(res['tvdbId'])
        poster = (res['remotePoster'])
        break
    show = sonarr.get_series(tvdb_id=id)
    await ctx.send(poster)
    show_path = config['API']['show_path']
    await ctx.send("Is this correct? Just type yes or no.")
    def check(m):
        return m.content.lower() in ("yes", "no") and m.channel == ctx.channel
    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Timed out, please try again.")
    else:
        if msg.content.lower() == "yes":
            try:
                show.add(show_path,quality_profile,language)
                await ctx.send(f"Added show to sonarr library: {show}")
            except:
                await ctx.send(f"Failed to add {show}. Maybe its already in the sonarr library? \nIf no results, try changing your search term.")
        else:
            await ctx.send("Cancelled.")
            
#help command            
@bot.command(aliases=['h','H','Help'])
async def bothelp(ctx):
        await ctx.send("Add any movie or show by sending a command!")
        await ctx.send("To add a movie use !m or !movie, if result is not as expected, iterate through search with a number I.E. \"!m thirteen ghosts 2\", this will use the second option returned and so on. bot will direct message when movie is available on plex.")
        await ctx.send("to add a show use !s or !show. iteration needs to be added. bot will direct message when show is available on plex.") 
        

# run the bot "main"
async def main():
    async with bot:
        bot.loop.create_task(recently())
        recently.start()
        await bot.start(TOKEN)
asyncio.run(main())
