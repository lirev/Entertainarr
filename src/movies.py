import discord
from plexapi.myplex import MyPlexAccount
from discord.ext import commands, tasks
from arrapi import RadarrAPI, SonarrAPI
from pyarr import SonarrAPI as sapi
from tmdbv3api import TMDb, TV, Movie as M
import configparser
import os
import datetime
import time
import asyncio
import requests
import traceback

#discord intents, manages bot "permissions"
intents = discord.Intents.default()  # or .all() if you ticked all, that is easier
intents.typing = True
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)  # intialization of bot and "Import" the intents
last_movie = None
user = None


# Load the configuration file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)

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

#tdmb
m = M()
tmdb=TMDb()
tmdb_url ='https://image.tmdb.org/t/p/w500/'
tmdb_api = config['API']['tmdb_api']
tmdb_Rapi = config['API']['tmdb_Rapi']
tmdb.api_key=tmdb_api
tmdb.language = 'en'
channel_id = config['API']['channel_id']

quality_profile = config['API']["quality_profile"]

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

def setup(bot):
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
        if result_number == 1:
            await ctx.send(f"Searching Radarr for {title}.")       
        else:
            await ctx.send(f"Searching Radarr for {title} with increment {result_number}.")
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
                except Exception as e:
                    # Log or print the error details
                    error_details = traceback.format_exc()
                    await ctx.send(f"Failed to add {movie}. Maybe its already in the radarr library? \nIf no results, try changing your search term.")
                    print(f"{str(e)}\n\n{error_details}")
            else:
                await ctx.send("Cancelled.")