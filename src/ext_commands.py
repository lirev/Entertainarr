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

def setup(bot):
    @bot.command(aliases=['n', 'new'])
    async def show_new_movies(ctx):
        # Prompt the user to choose between shows, movies, or both
        await ctx.send("Which category of new releases would you like to see?\n1. Movies\n2. Shows\n3. Both")
        
        def check_category(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['1', '2', '3']
        
        try:
            category_msg = await bot.wait_for("message", check=check_category, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("Timed out, please try again.")
            return
        
        category = category_msg.content.lower()
        
        if category == '1':
            await show_newly_released_movies(ctx)
        elif category == '2':
            await show_newly_released_shows(ctx)
        elif category == '3':
            await show_newly_released_movies(ctx)
            await show_newly_released_shows(ctx)
            
        
    async def show_newly_released_movies(ctx):
        # Calculate the date range for the past 7 days
        today = datetime.date.today()
        past_week = today - datetime.timedelta(days=7)
        today_str = today.isoformat()
        past_week_str = past_week.isoformat()

        await ctx.send("Newly released Movies")
        # Set the API endpoint URL
        url = 'https://api.themoviedb.org/3/discover/movie'

        # Set the query parameters
        params = {
            'include_adult': 'false',
            'include_video': 'false',
            'language': 'en-US',
            'sort_by': 'release_date.desc',
            'primary_release_date.gte': past_week_str,
            'primary_release_date.lte': today_str,
            'region': 'US'
        }

        # Set the authorization header with your API access token
        headers = {
            'Authorization': 'Bearer '+ tmdb_Rapi,
            'accept': 'application/json'
        }

        # Make the GET request
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        # Extract movie titles and thumbnails from the response
        movies = data['results']
        movie_list = []
        for movie in movies:
            title = movie['title']
            thumbnail = f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}"
            description = movie['overview']
            movie_list.append({'title': title, 'thumbnail': thumbnail, 'description': description})

        if len(movie_list) > 0:
            # Send the response with thumbnails
            for movie in movie_list:
                title = movie['title']
                thumbnail = movie['thumbnail']
                description = movie['description']
                embed = discord.Embed(title=title, description=description)
                embed.set_thumbnail(url=thumbnail)
                await ctx.send(embed=embed)
        else:
            await ctx.send("No movies released in the last 7 days.")
            
        await ctx.send("Done displaying newly released movies.")


    async def show_newly_released_shows(ctx):
        await ctx.send("Newly released TV Shows")
        url = f'https://api.themoviedb.org/3/discover/tv?include_adult=false&language=en-US&page=1&sort_by=popularity.desc&first_air_date.gte={get_past_week_date()}&first_air_date.lte={get_current_date()}&watch_region=US&api_key={tmdb_api}'
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            shows = data['results']
            
            if shows:
                for show in shows:
                    title = show['name']
                    thumbnail = get_thumbnail_url(show['poster_path'])
                    description = show['overview']
                    
                    embed = discord.Embed(title=title, description=description)
                    embed.set_thumbnail(url=thumbnail)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("No TV shows released in the United States in the last 7 days.")
        else:
            await ctx.send("Failed to retrieve newly released TV shows.")
            
        await ctx.send("Done displaying newly released shows.")

    def get_current_date():
        return datetime.date.today().strftime('%Y-%m-%d')

    def get_past_week_date():
        past_week = datetime.date.today() - datetime.timedelta(days=7)
        return past_week.strftime('%Y-%m-%d')

    def get_thumbnail_url(poster_path):
        base_url = 'https://image.tmdb.org/t/p/w500'
        return base_url + poster_path if poster_path else None
