"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for mongodb database interaction.
"""

import asyncio
import discord
import stwutil as stw
import copy
import inspect


async def insert_default_document(client, user_snowflake):
    """
    Inserts a default document into the database.

    Args:
        client (discord.ext.commands.Bot): The bot client.
        user_snowflake: The user snowflake to insert the document for.

    Returns:
        dict: The default document.
    """
    default_document = copy.deepcopy(client.user_default)
    default_document['user_snowflake'] = user_snowflake
    try:
        del default_document["_id"]
    except KeyError:
        pass
    await client.stw_database.insert_one(default_document)

    return default_document


async def replace_user_document(client, document):
    """
    Replaces a user document in the database.

    Args:
        client: The bot client.
        document: The document to replace.
    """

    snowflake = document["user_snowflake"]

    client.profile_cache[snowflake] = document
    await client.stw_database.replace_one({"user_snowflake": snowflake}, document)


async def get_autoclaim_user_cursor(client):
    """
    Gets the autoclaim user cursor.

    Args:
        client: The bot client.

    Returns:
        pymongo.cursor.Cursor: The autoclaim user cursor.
    """
    return client.stw_database.find({"auto_claim": {"$ne": None}})


async def get_accounts_with_auth_data_cursor(client):
    """
    Gets a cursor of all accounts with any profile with auth data.

    Args:
        client: The bot client.

    Returns:
        pymongo.cursor.Cursor: The autoclaim user cursor.
    """
    return client.stw_database.find({"profiles": {"$ne": None}})


async def count_of_accounts_to_autoclaim(client):
    """
    Gets the autoclaim user count

    Args:
        client: The bot client.

    Returns:
        int: The autoclaim user count.
    """
    return client.stw_database.count_documents({"auto_claim": {"$ne": None}})


async def check_profile_ver_document(client, document):
    """
    Checks the profile version of a document and updates it if necessary.

    Args:
        client: The bot client.
        document: The document to check.

    Returns:
        dict: The updated document.
    """
    current_profile_ver = client.user_default["global"]["profiles_ver"]
    force_overwrite = client.user_default["global"]["rewrite_older"]
    user_id = document["user_snowflake"]

    try:
        if document["global"]["profiles_ver"] >= current_profile_ver:
            return document

    except KeyError:
        pass

    if not force_overwrite:
        copied_default = copy.deepcopy(client.user_default)
        new_base = await asyncio.gather(asyncio.to_thread(deep_merge, copied_default, document))
        new_base = new_base[0]
        for profile in list(new_base["profiles"].keys()):
            new_base["profiles"][profile] = await asyncio.gather(
                asyncio.to_thread(deep_merge, copied_default["profiles"]["0"], new_base["profiles"][profile]))
    else:
        new_base = copy.deepcopy(client.user_default)
        new_base['user_snowflake'] = user_id

    new_base["global"]["profiles_ver"] = current_profile_ver

    await replace_user_document(client, new_base)
    return new_base


def generate_profile_select_options(client, current_selected_profile, user_document):
    """
    Generates a list of profile select options for a user.

    Args:
        client: The bot client.
        current_selected_profile: The currently selected profile.
        user_document: The user document.

    Returns:
        list: A list of profile select options.
    """
    select_options = []

    if current_selected_profile is None:
        select_options.append(discord.SelectOption(
            label="No Profiles :(",
            value="None",
            default=False,
            emoji=client.config["emojis"]["error"]
        ))

    for profile in user_document["profiles"]:

        profile = user_document["profiles"][profile]

        # this var does nothing :3
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
    """
    Deep merges two dictionaries.

    Args:
        dict1: The first dictionary.
        dict2: The second dictionary.

    Returns:
        dict: The merged dictionary.
    """

    def _val(value_1, value_2):
        if isinstance(value_1, dict) and isinstance(value_2, dict):
            return deep_merge(value_1, value_2)
        return value_2 or value_1

    return {key: _val(dict1.get(key), dict2.get(key)) for key in dict1.keys() | dict2.keys()}


# define function to read mongodb database and return a list of all the collections in the database
async def get_user_document(ctx, client, user_snowflake, silent_error=False):
    """
    Gets a user document from the database.

    Args:
        ctx: The context.
        client: The bot client.
        user_snowflake: The user snowflake to get the document for.
        silent_error: Whether to silently error or not.

    Returns:
        dict: The user document.
    """

    error_check = await stw.processing_queue_error_check(client, ctx, user_snowflake)

    if error_check is not True:

        if not silent_error:
            await stw.slash_send_embed(ctx, embeds=error_check)
        print(f"{user_snowflake} STUCK IN PROCESSING USER DOCUMENT?")
        return False

    update_cache = False
    try:
        document = client.profile_cache[user_snowflake]
    except:
        document = await client.stw_database.find_one({'user_snowflake': user_snowflake})
        update_cache = True

    if document is None:
        document = await insert_default_document(client, user_snowflake)
        update_cache = True

    document = await check_profile_ver_document(client, document)

    if not update_cache:
        client.profile_cache[user_snowflake] = document

    return document


async def timeout_check_processing(view, client, interaction):
    """
    Checks if a user is stuck in the processing queue.

    Args:
        view: The view.
        client: The bot client.
        interaction: The interaction.

    Returns:
        bool: True if the user is stuck in the processing queue, False if not.
    """
    if view.ctx.author.id == interaction.user.id:
        if interaction.user.id in client.processing_queue:
            view.ctx = interaction
            await view.on_timeout()
            return False
    return True


async def active_view(client, user_snowflake, view):
    """
    Checks if a user has an active view.

    Args:
        client: The bot client.
        user_snowflake: The user snowflake to check.
        view: The view to check for.
    """
    client.active_profile_command[user_snowflake] = view


async def command_counter(client, user_snowflake):
    """
    Counts the number of commands a user has active.

    Args:
        client: The bot client.
        user_snowflake: The user snowflake to check.
    """
    try:
        old_view = client.active_profile_command[user_snowflake]
        await old_view.on_timeout()
        del client.active_profile_command[user_snowflake]
    except Exception as E:
        print(f"{E}")
        pass
