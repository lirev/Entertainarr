import discord
from discord.ext import commands
from arrapi import RadarrAPI, SonarrAPI
from pyarr import SonarrAPI as sapi
from tmdbv3api import TMDb, TV, Movie as M
import configparser
import os
import datetime
import time
import asyncio
import requests

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

#tdmb
m = M()
tmdb=TMDb()
tmdb_url ='https://image.tmdb.org/t/p/w500/'
tmdb_api = config['API']['tmdb_api']
tmdb_Rapi = config['API']['tmdb_Rapi']
tmdb.api_key=tmdb_api
tmdb.language = 'en'
channel_id = config['API']['channel_id']

quality_profile = config['API']['quality_profile']
language = config['API']['language']

def setup(bot):
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