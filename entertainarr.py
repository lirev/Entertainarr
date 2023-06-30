import discord
from discord.ext import commands, tasks
from plexapi.myplex import MyPlexAccount
from arrapi import RadarrAPI, SonarrAPI
from pyarr import SonarrAPI as sapi
from tmdbv3api import TMDb, TV, Movie as M
import os
import ctxcore
import asyncio
import json
import configparser
import requests
import datetime

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
tmdb_Rapi = config['API']['tmdb_Rapi']
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






# run the bot "main"
async def main():
    async with bot:
        bot.loop.create_task(recently())
        recently.start()
        await bot.start(TOKEN)
asyncio.run(main())
