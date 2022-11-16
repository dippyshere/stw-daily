# mongo interaction

import asyncio
import json
import os
import discord
import discord.ext.commands as ext
from discord import Option, slash_command

import stwutil as stw

# did u install motor no :) :( :c oh lmao sorry racism
# access monogodb async

import motor.motor_asyncio


async def insert_default_document(client, user_snowflake):
    default_document = client.user_default
    default_document['user_snowflake'] = user_snowflake
    await client.stw_database.insert_one(default_document)

    return default_document


async def replace_user_document(client, document):
    await client.stw_database.replace_one({"user_snowflake": document["user_snowflake"]}, document)


async def check_profile_ver_document(client, document):
    current_profile_ver = client.user_default["global"]["profiles_ver"]
    force_overwrite = client.user_default["global"]["rewrite_older"]
    user_id = document["user_snowflake"]

    try:
        if document["global"]["profiles_ver"] >= current_profile_ver:
            return document

    except KeyError:
        pass

    if force_overwrite == False:
        copied_default = client.user_default.copy()
        new_base = await asyncio.gather(asyncio.to_thread(deep_merge, copied_default, document))
        new_base = new_base[0]
        for profile in list(new_base["profiles"].keys()):
            new_base["profiles"][profile] = await asyncio.gather(
                asyncio.to_thread(deep_merge, copied_default["profiles"]["0"], new_base["profiles"][profile]))
    else:
        new_base = client.user_default
        new_base['user_snowflake'] = user_id

    new_base["global"]["profiles_ver"] = current_profile_ver

    await replace_user_document(client, new_base)
    return new_base

def generate_profile_select_options(client, current_selected_profile, user_document):
    select_options = []

    if current_selected_profile is None:
        select_options.append(discord.SelectOption(
            label="No Available Profiles!",
            value="None",
            default=False,
            emoji=client.config["emojis"]["error"]
        ))

    for profile in user_document["profiles"]:

        profile = user_document["profiles"][profile]

        selected = False
        profile_id = profile["id"]
        if profile_id == current_selected_profile:
            selected = True

        profile_id = str(profile_id)
        select_options.append(discord.SelectOption(
            label=profile["friendly_name"],
            value=profile_id,
            default=False,
            emoji=client.config["emojis"][profile_id]
        ))

    return select_options

# you are zoommin :(((   ong ok bye have fun i am having the fun PLEASE WAIT HOST IS WORKING WITH A SETTINGS DIALOG
def deep_merge(dict1, dict2):
    def _val(value_1, value_2):
        if isinstance(value_1, dict) and isinstance(value_2, dict):
            return deep_merge(value_1, value_2)
        return value_2 or value_1

    return {key: _val(dict1.get(key), dict2.get(key)) for key in dict1.keys() | dict2.keys()}


# define function to read mongodb database and return a list of all the collections in the database
async def get_user_document(client, user_snowflake):
    # which one lol
    # what do u want to call the database and collection? actually we can just slap this into config too :) sure
    document = await client.stw_database.find_one({'user_snowflake': user_snowflake})

    if document is None:
        document = await insert_default_document(client, user_snowflake)

    document = await check_profile_ver_document(client, document)
    return document
