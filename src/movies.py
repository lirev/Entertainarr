import discord
from plexapi.myplex import MyPlexAccount
from discord.ext import commands, tasks
from arrapi import RadarrAPI
import configparser
import os
import datetime
import time
import aiohttp
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

error_id = config['API']['error_id']

# Load the configuration file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)

#radarr
host_url = config['API']['host_url']
api_key = config['API']['api_key']
radarr = RadarrAPI(host_url, api_key)

#plex
plexUser = config['API']['plexUser']
plexPass = config['API']['plexPass']
plexServer = config['API']['plexServer']
account = MyPlexAccount(plexUser, plexPass)
plex = account.resource(plexServer).connect() 
channel_id = config['API']['channel_id']
quality_profile = config['API']["quality_profile"]
rapi_key = config['API']['tmdb_Rapi']

def setup(bot):
    @bot.command(aliases=['m', 'M', 'Movie'])
    async def movies(ctx, *, title):
        global user
        user = ctx.author
        # Split input string into title and increment number
        parts = title.split('#')
        title = parts[0].strip()
        increment_str = parts[1].strip() if len(parts) > 1 else '1'
        result_number = int(increment_str)
        if result_number > 10 or result_number < 1:
            await ctx.send("Invalid result number, please enter a number within the range of search results.")
            return
        if result_number == 1:
            await ctx.send(f"Searching Radarr for {title}.")       
        else:
            await ctx.send(f"Searching Radarr for {title} with increment {result_number}.")

        try:
            search_results = radarr.search_movies(title)
            if not search_results:
                await ctx.send("No movies found.")
                return
            # Get the specific result based on the result number
            movie = search_results[result_number - 1]
            url = f"https://api.themoviedb.org/3/movie/{movie.tmdbId}/images"

            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {rapi_key}"  # Replace with your actual token
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        posters = data.get('posters', [])
                        if posters:
                            for poster in posters:
                                poster_path = poster.get('file_path')
                                full_poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                                await ctx.send(full_poster_url)
                                break
                        else:
                            await ctx.send("No posters found.")
                    else:
                        print(f"Error: {response.status} - {await response.text()}")
                        await ctx.send("Failed to fetch movie poster.")
            movie_path = config['API']['movie_path']
            await ctx.send("Is this correct? Just type yes or no.")

            def check(m):
                return m.content.lower() in ("yes", "no") and m.channel == ctx.channel
            msg = await bot.wait_for("message", check=check, timeout=30)
            if msg.content.lower() == "yes":
                try:
                    radarr.add_movie(tmdb_id=movie.tmdbId, quality_profile=quality_profile, root_folder=movie_path)
                    await ctx.send(f"Added movie to Radarr library: {movie.title}")
                except Exception as e:
                    await ctx.send(f"Failed to add {movie.title}. Maybe it's already in the Radarr library? \nIf no results, try changing your search term.")
                    await error_message(e, bot)
            else:
                await ctx.send("Cancelled.")
        except Exception as e:
            await error_message(e, bot)

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


async def error_message(e, bot):
    try:
        error_channel = await bot.fetch_channel(error_id)
        print(error_id)
        await error_channel.send(f"An exception occurred: \n{str(e)}")
        print("Error message sent successfully.")
    except Exception as send_err:
        print(f"Failed to send the error message: {str(send_err)}")