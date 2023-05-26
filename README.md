# Entertainarr
This is a simple script used to create a discord bot for managing you media files through radarr, sonarr, and plex.

Setup is not plug and play, requires install and knowledge of things like sonarr, radarr, jackett, and plex. requires multiple api keys.

Im sure a few things could be changed but it currently works how i need it to and havent touched it much. 

Setup:
  record all credentials/keys into config.ini
  
  Install sonarr and radarr on the main server. i used a windows 10 install nothing fancy. record your IP address for the server and Api key for both sonarr and radarr.
  
  Setup jackett for sonarr and radarr, i will not explain this. 
  
  Create a discord bot through the discord developer website, give your bot permissions to send and read messages. make sure to check the box for "MESSAGE CONTENT INTENT".
  
  I will not explain the install for a plex server, record your username, password and the name given to the plex server, something like HOME-SERVER. install on same device as 
 radarr and sonarr
 
  Get a TMDB api key for searching for titles. 
  
  Sonarr and radarr should be setup to have their own file locations, for example Z:/entertainment/shows and Z:/entertainment/movies. if using a download client for radarr and sonarr, create a seperate tag in your client profile to seperate files. for example radarr client gets the catagory "radarr".
  
  the discord channel id you want the bot to send messages to, if you want the bot in multiple servers a few lines will need to be replicated in the code.
  

Once bot setup is complete, a user can search the radarr or sonarr api for titles and add them to your list. 


Use: enter "!m the hunger games" in the discord channel where the bot has access and follow the prompts. 
![image](https://github.com/lirev/Entertainarr/assets/97287390/bb469ae8-941a-4e67-9ab8-72666f57f352)

