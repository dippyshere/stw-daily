print("Starting STW Daily")


import asyncio
import aiohttp
import math
import random
import re
import os
import sys
import psutil
import datetime
import time
import stwutil as stw
import items
import timeit
import json
import logging

import discord
import discord.ext.commands as ext
from discord.ext import tasks
from discord import Option
    
# Compatability layer for future versions of python 3.11+ 
try:
    import tomllib as toml
except ModuleNotFoundError:
    
    import tomli as toml

client = ext.AutoShardedBot(command_prefix=ext.when_mentioned, case_insensitive=True)

def load_config(config_path):
    with open(config_path,"rb") as config_file:
        config = toml.load(config_file)
        config_file.close()

    return config

def main():
    
    # Loading config file
    config_path = "config.toml"    
    client.config = load_config(config_path)

    # simple way to parse the colours from config into usable colours
    client.colours = {}
    for name, colour  in client.config["colours"].items():
        client.colours[name] = discord.Colour.from_rgb(colour[0], colour[1], colour[2])

    client.temp_auth = {}
    client.remove_command('help')


    #list of extensions for stw daily to load in
    extensions = [
        "reward",
        "help",
        "auth",
        "daily",
        "info",
        "research",
        ]

    # load the extensions
    for ext in extensions:
        print(client.load_extension(f"ext.{ext}"))

    update_status.start()
    dailyreminder.start()
    client.run(f"{os.environ['STW_DAILY_TOKEN']}")
    
async def create_http_session():
    return aiohttp.ClientSession()
    
# basic information for you <33
@client.event
async def on_ready():
    client.stw_session = await create_http_session();
    print("Started STW Daily")

# simple task which updates the status ever 60 seconds to display time until next day/reset
@tasks.loop(seconds=60)
async def update_status():  
    await client.wait_until_ready()
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name=f"@{client.user.name}  |  Reset in: \n{stw.time_until_end_of_day()}\n  |  In {len(client.guilds)} guilds"))
                                  
# a simple task to support the reminder for STW Dailies server (blame dippyshere for the logic of this :D )
def is_me(m):
    return m.author == client.user
@tasks.loop(seconds=60)
#skuby was here
async def dailyreminder():
    await client.wait_until_ready()
    if str(datetime.datetime.utcnow().replace(second=0, microsecond=0).time()) == "00:00:00":
        channel = client.get_channel(767607876348018689)
        await channel.purge(limit=2, check=is_me)
        embed = discord.Embed(title='Daily reminder:', description=f'You can now claim today\'s daily reward. \n Next daily reminder <t:{int(datetime.datetime.combine(datetime.datetime.utcnow() + datetime.timedelta(days=1), datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).timestamp())}:R>.',
                      colour=discord.Colour.blue())
        embed.add_field(name='Item shop:', value='[fnbr.co/shop](https://fnbr.co/shop)', inline=True)
        embed.add_field(name='\u200b', value='\u200b')
        embed.add_field(name='Mission alerts:', value='[seebot.dev/missions.php](https://seebot.dev/missions.php)', inline=True)
        embed.add_field(name='Auth code link:', value='[epicgames.com/id/api/redirect...](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)', inline=True)
        embed.add_field(name='\u200b', value='\u200b')
        embed.add_field(name='Claiming channel:', value='<#757768833946877992>', inline=True)                           
        embed.set_thumbnail(
    url='https://cdn.discordapp.com/attachments/748078936424185877/924999902612815892/infostwdaily.png')
        embed.set_footer(text=f"This is an automated daily reminder from {client.user.name}"
                         , icon_url=client.user.avatar.url)
        await channel.send("<@&956005357346488341>", embed=embed)
#skuby left here

if __name__ == "__main__":
    main()
    
