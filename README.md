# Entertainarr
This is a simple script used to create a discord bot for adding titles to radarr, sonarr, and plex.

Setup is some-what plug and play, requires install and knowledge of things like sonarr, radarr, jackett, and plex. Requires multiple api keys.

Im sure a few things could be changed, but it currently works how i need it to and havent touched it much. I welcome tips and reccomendations, I am not a professional. 

Setup:
  1. record all credentials/keys into config.ini
  
  2. Install sonarr and radarr on the main server. I used a windows 10 install, nothing fancy. Record your IP address for the server and API key for both sonarr and radarr.
  
  3. (optional) Setup jackett for sonarr and radarr, I will not explain this. 
  
  4. Create a discord bot through the discord developer website, give your bot permissions to send and read messages. Make sure to check the box for "MESSAGE CONTENT INTENT".
  
  5. I will not explain the install for a plex server, record your username, password and the name given to the plex server. Something like HOME-SERVER, install on same device as 
 radarr and sonarr
 
  6. Get a TMDB api key for searching for titles. 
  
  7. Sonarr and radarr should be setup to have their own file locations, for example Z:/entertainment/shows and Z:/entertainment/movies. If using a download client for radarr and sonarr, create a seperate tag in your client profile to seperate files. For example radarr client gets the catagory "radarr".
  
  8. The discord channel id you want the bot to send messages to, If you want the bot in multiple servers a few lines will need to be replicated in the code.

  9. If all goes well all you need to do is run the python script and the bot should appear and be ready for testing. I have the bot run from a linux server as a service. an auto start can be created for windows if you want all functions of this to run on 1 device.  
  

Once bot setup is complete, a user can search the radarr or sonarr api for titles and add them to your list. 


Use: enter "!m the hunger games" in the discord channel where the bot has access and follow the prompts. 
![241129845-bb469ae8-941a-4e67-9ab8-72666f57f352](https://github.com/user-attachments/assets/761485c1-7b0d-4517-9651-08c4f3718340)


