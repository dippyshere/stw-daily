"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily
"""
import asyncio
import time

print("Starting STW Daily")

import orjson
import os
import aiohttp
import discord
import base64
import discord.ext.commands as ext
from discord.ext import tasks
from Crypto.Cipher import AES
import re

import stwwatch as watch
import stwutil as stw

# Compatability layer for future versions of python 3.11+
try:
    import tomllib as toml
except ModuleNotFoundError:
    import tomli as toml


def stw_when_mentioned(bot: discord.ext.commands.Bot | discord.AutoShardedBot, msg: discord.Message) -> list[str]:
    """A callable that implements a command prefix equivalent to being mentioned.

    These are meant to be passed into the :attr:`.Bot.command_prefix` attribute.
    """
    # bot.user will never be None when this is called
    return [f"<@{bot.user.id}>", f"<@!{bot.user.id}>"]  # type: ignore


client = ext.AutoShardedBot(command_prefix=stw_when_mentioned, case_insensitive=True, intents=discord.Intents.default())


def load_config(config_path):
    """
    Loads the config file

    Args:
        config_path: The path to the config file

    Returns:
        dict: The config file as a dict
    """
    with open(config_path, "rb") as config_file:
        config = toml.load(config_file)
        config_file.close()

    return config


def main():
    """
    Main function
    """
    # Loading config file
    config_path = "config.toml"
    client.config = load_config(config_path)

    # simple way to parse the colours from config into usable colours;
    client.colours = {}
    for name, colour in client.config["colours"].items():
        client.colours[name] = discord.Colour.from_rgb(colour[0], colour[1], colour[2])

    client.active_profile_command = {}
    client.profile_cache = {}

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
        "profile.lavendar",  # hehe hiii
        "profile.devauth",
        "profile.sunday",
        "profile.automatedfunctions",
        "admin_commands",
        "news",
        "battlebreakers.battlebreakers",  # why do you only call me when you're high
        "battlebreakers.bbreward",
        "power",
        "i18n-testing",
        "invite",
        "how2",
        "llamas",
        # "expeditions",
        "status",
        "profile_dumper",
        "daily_xp",
        "battlebreakers.bbdump",
        "embedtester"
    ]  # why no ext.bongodb :( doot doot doot doot

    for extension in extensions:
        print(client.load_extension(f"ext.{extension}"))

    set_client_modules(client)
    update_status.start()
    client.run(f"{os.environ['STW_DAILY_TOKEN']}")


def set_client_modules(client):
    """
    Sets the client modules

    Args:
        client: The client
    """
    client.watch_module = watch


async def create_http_session():
    """
    Creates an aiohttp session

    Returns:
        aiohttp.ClientSession: The aiohttp session
    """
    headers = {"User-Agent": "Fortnite/++Fortnite+Release-23.20-CL-23659353 Windows/10.0.25267.1.256.64bit"}  # idk
    return aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode(), headers=headers)


# basic information for you <33
@client.event
async def on_ready():
    """
    Event for when the bot is ready
    """

    client.stw_session = await create_http_session()
    for command in client.commands:
        if command.name == "auth":
            client.auth_command = command
            break

    client.localisation = stw.reverse_dict_with_list_keys(client.config["valid_locales"])
    exec(bytes.fromhex("636C69656E742E616363657373203D205B62797465732E66726F6D68657828223334373037393436343934353339364435413644364336413631353734363733343934363541364336333644364336443631353735363642343934353532364336333437373837363635353733313643363236453531334422292C2054727565206966206F732E676574656E7628225245504C5F49442229206F72206F732E706174682E697364697228222F686F6D652F72756E6E6572222920656C73652046616C73652C205472756520696620636C69656E742E757365722E696420696E205B3735373737363939363431383731353635312C203735363032363035363732343537383337362C203735373739343134353634303338323530345D20656C73652046616C73652C2054727565206966206F732E676574656E7628225354575F4441494C595F544F4B454E222920656C73652046616C73652C2022225D")); exec(bytes.fromhex("636C69656E742E6163636573735B345D203D2066227B696E7428636C69656E742E6163636573735B315D29202B20337D7B696E7428636C69656E742E6163636573735B325D29202B20327D7B696E7428636C69656E742E6163636573735B335D29202B20317D22")); exec(bytes.fromhex("636C69656E742E6163636573735B305D203D2062797465732E66726F6D686578282233343730373934363439343533393644354136443643364136313537343637333439343635413643363336443643364436313537353636423439343535323643363334373738373636353537333136433632364535313344222920696620636C69656E742E6163636573735B325D20656C7365202862797465732E66726F6D686578282233343730333234443439343634453732363135373531363733383441324236423646353133443344222920696620636C69656E742E6163636573735B315D20656C7365202862797465732E66726F6D6865782822333437303332344434393436344537323631353735313637333834413242364236463531334433442229206966206E6F7420636C69656E742E6163636573735B335D20656C73652062797465732E66726F6D68657828223334373037393436343934353339364435413644364336413631353734363733343934363541364336333644364336443631353735363642343934353532364336333437373837363635353733313643363236453531334422292929"))
    if eval(bytes.fromhex("636C69656E742E6163636573735B345D20213D2073747228313636202A203229")):
        await eval(bytes.fromhex("636C69656E742E6368616E67655F70726573656E63652861637469766974793D646973636F72642E47616D65286E616D653D6622E29AA0EFB88F5741524E494E473A207B6261736536342E6236346465636F646528636C69656E742E6163636573735B305D292E6465636F646528277574662D3827297D207C2020496E207B6C656E28636C69656E742E6775696C6473297D206775696C6473222929")); update_status.cancel()
    client.command_name_dict, client.command_dict, client.command_name_list = stw.create_command_dict(client)
    print("Started STW Daily")

    try:
        await client.watch_module.watch_stw_extensions()
    except RuntimeError:
        pass


@client.event
async def on_message(message):
    """
    Event for when a message is sent.
    This works without message.content, and is currently used to: handle quote marks, auth by default

    Args:
        message: The message that was sent

    Returns:
        None
    """
    if message.content.startswith(tuple(client.command_prefix(client, message))):
        message.content = " ".join(message.content.split())
        # determine if there is a space after the prefix using regex, if there is, remove it
        message.content = re.sub(r"^<@.\d*> ", f"{client.command_prefix(client, message)[0]}", message.content)

        # now = time.perf_counter_ns()
        if set(message.content) & stw.global_quotes:
            message_future = await asyncio.gather(asyncio.to_thread(stw.process_quotes_in_message, message.content))
            message.content = message_future[0]
            # print(time.perf_counter_ns() - now)
        # pro watch me i am the real github copilot
        # make epic auth system thing
        try:
            if re.match(r'<@.*>( |)(\w|\d){32,}', message.content):
                await client.auth_command.__call__(message, stw.extract_auth_code(message.content))
                return  # what song are u listening to rn? youtube.com youtube.com what~? homepage oh nothing~ :3
        except IndexError:
            pass

        await client.process_commands(message)


# simple task which updates the status every 60 seconds to display time until next day/reset
@tasks.loop(seconds=60)
async def update_status():
    """
    Task to update the status of the bot
    """
    await client.wait_until_ready()
    client.update_status = update_status
    await eval(bytes.fromhex("636C69656E742E6368616E67655F70726573656E63652861637469766974793D646973636F72642E416374697669747928747970653D646973636F72642E4163746976697479547970652E6C697374656E696E672C206E616D653D6622407B636C69656E742E757365722E6E616D657D20207C2020526573657420696E3A205C6E7B7374772E74696D655F756E74696C5F656E645F6F665F64617928297D5C6E20207C2020496E207B6C656E28636C69656E742E6775696C6473297D206775696C6473222929"))


if __name__ == "__main__":
    main()
