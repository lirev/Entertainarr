import discord
from discord.ext import commands
from wakeonlan import send_magic_packet  
import configparser
import os

# Load the configuration file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)

#discord intents, manages bot "permissions"
intents = discord.Intents.default()  # or .all() if you ticked all, that is easier
intents.typing = True
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)  # intialization of bot and "Import" the intents
user = None

# Read admin and mac_address from the config
#wake
admin = str(config['API']['admin'])
# Dictionary of devices
devices = {
    "Desktop": config['API']['desk'],  # Update with your device names and MACs
    "Kali": config['API']['kali'],
    # Add more devices here
}
def setup(bot):
    # Command to send Wake on LAN only if the command is sent by an admin
    @bot.command(aliases=['rw'])
    async def wake(ctx):
        try:
            if str(ctx.author.id) == str(admin):
                # Construct the list of devices for the user to choose from
                device_list = "\n".join([f"{index + 1}. {device}" for index, device in enumerate(devices.keys())])
                await ctx.send(f"Select a device to send the magic packet to:\n{device_list}")
                
                # Wait for the user's response
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                user_response = await ctx.bot.wait_for('message', check=check, timeout=30)
                selected_device_index = int(user_response.content) - 1
                
                selected_device = list(devices.keys())[selected_device_index]
                selected_mac_address = devices[selected_device]
                
                send_magic_packet(selected_mac_address)
                
                await ctx.send(f"Sent magic packet to {selected_device}")
            else:
                await ctx.send("You are not authorized to use this command.")
        except Exception as e:
            print(f"An error occurred while sending magic packet: {e}")
