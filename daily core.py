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
        "reminder",
        ]

    # load the extensions
    for ext in extensions:
        print(client.load_extension(f"ext.{ext}"))

    update_status.start()
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


if __name__ == "__main__":
    main()
    
