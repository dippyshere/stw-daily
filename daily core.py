print("Starting STW Daily")

import os
import aiohttp
import discord
import discord.ext.commands as ext
from discord.ext import tasks

import stwutil as stw

# Compatability layer for future versions of python 3.11+ 
try:
    import tomllib as toml
except ModuleNotFoundError:
    import tomli as toml

client = ext.AutoShardedBot(command_prefix=ext.when_mentioned, case_insensitive=True)


def load_config(config_path):
    with open(config_path, "rb") as config_file:
        config = toml.load(config_file)
        config_file.close()

    return config


def main():
    # Loading config file
    config_path = "config.toml"
    client.config = load_config(config_path)

    # simple way to parse the colours from config into usable colours;
    client.colours = {}
    for name, colour in client.config["colours"].items():
        client.colours[name] = discord.Colour.from_rgb(colour[0], colour[1], colour[2])

    client.temp_auth = {}
    client.remove_command('help')

    # list of extensions for stw daily to load in
    extensions = [
        "reward",
        "help",
        "auth",
        "daily",
        "info",
        "research",
        "serverext",
        "homebase",
        "vbucks",
        "reload",
        "profile.lavendar",
        "profile.devauth",
        "profile.sunday",
        "news",
        "battlebreakers.battlebreakers",  # why do you only call me when you're high
        "battlebreakers.bbreward",
        "power",
    ]  # why no ext.bongodb :( doot doot doot doot
    # load the extensions
    client.a = "✅ Official Verified Deployment", True  # seleckted
    for ext in extensions:
        print(client.load_extension(f"ext.{ext}"))

    update_status.start()
    client.run(f"{os.environ['STW_DAILY_TOKEN']}")


async def create_http_session():
    return aiohttp.ClientSession()


# basic information for you <33
@client.event
async def on_ready():
    client.stw_session = await create_http_session()
    client.command_name_dict, client.command_dict, client.command_name_list = stw.create_command_dict(client)
    print("Started STW Daily")


@client.event
async def on_message(message):
    if '"' in message.content:
        message = stw.process_quotes_in_message(message)

    await client.process_commands(message)


# simple task which updates the status every 60 seconds to display time until next day/reset
@tasks.loop(seconds=60)
async def update_status():
    await client.wait_until_ready()
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name=f"@{client.user.name}  |  Reset in: \n{stw.time_until_end_of_day()}\n  |  In {len(client.guilds)} guilds"))


if __name__ == "__main__":
    main()
