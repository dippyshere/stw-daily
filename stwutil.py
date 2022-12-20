"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the main utility library for stw daily. It contains a lot of functions that are used throughout the bot.
"""
import base64
import datetime
import os
import random
import re
import time
import math
from difflib import SequenceMatcher

import blendmodes.blend
from Crypto.Cipher import AES
from PIL import Image
import asyncio
import io
import orjson

import discord

import items
import ext.battlebreakers.BBLootTable  # dinnerbrb its been much too long
from lang.stwi18n import I18n
from ext.profile.bongodb import get_user_document

with open("ext/battlebreakers/LoginRewards.json", "r") as f:
    LoginRewards = orjson.loads(f.read())
with open('ext/DataTables/SurvivorItemRating.json') as f:
    SurvivorItemRating = orjson.loads(f.read())
with open('ext/DataTables/HomebaseRatingMapping.json') as f:
    HomebaseRatingMapping = orjson.loads(f.read())
with open('ext/DataTables/ResearchSystem.json') as f:
    ResearchSystem = orjson.loads(f.read())
with open('ext/DataTables/AccountLevels.json') as f:
    AccountLevels = orjson.loads(f.read())
with open('ext/DataTables/BannerColorMap.json') as f:
    BannerColorMap = orjson.loads(f.read())
with open('ext/DataTables/BannerColors.json') as f:
    BannerColors = orjson.loads(f.read())
with open('ext/DataTables/STW_Accolade_Tracker.json') as f:
    max_daily_stw_accolade_xp = orjson.loads(f.read())[0]["Properties"]["MaxDailyXP"]
banner_d = Image.open("ext/homebase-textures/banner_texture_div.png").convert("RGB")
banner_m = Image.open("ext/homebase-textures/banner_shape_standard.png").convert("RGBA")

I18n = I18n()

# TODO: make this None (not a list)
guild_ids = [757765475823517851]


def reverse_dict_with_list_keys(dictionary):
    """
    Reverses a dictionary with list keys

    Args:
        dictionary: the dictionary to reverse

    Returns:
        A dictionary with the keys and values reversed
    """
    new_dict = {}

    for key, value in dictionary.items():
        for item in value:
            new_dict[item] = key

    return new_dict


async def view_interaction_check(view, interaction, command):
    """
    Checks if the interaction is created by the view author

    Args:
        view: the view
        interaction: the interaction
        command: the command

    Returns:
        True if the interaction is created by the view author, False if notifying the user

    """
    if view.ctx.author == interaction.user:
        return True
    else:
        try:
            already_notified = view.interaction_check_done[interaction.user.id]
        except:
            already_notified = False
            view.interaction_check_done[interaction.user.id] = True

        if not already_notified:

            support_url = view.client.config["support_url"]
            acc_name = ""
            error_code = "errors.stwdaily.not_author_interaction_response"
            embed = await post_error_possibilities(interaction, view.client, command, acc_name, error_code,
                                                   support_url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        else:
            return False


def edit_emoji_button(client, button):
    """
    Adds an emoji to a button

    Args:
        client: the client
        button: the button to add the emoji to

    Returns:
        The button with the emoji edited
    """
    button.emoji = client.config["emojis"][button.emoji.name]
    return button


def process_quotes_in_message(message):
    """
    Handles quotes in a message's content by replacing them with the appropriate unicode character

    Args:
        message: the message to process

    Returns:
        The processed message
    """
    # do not question the ways of the regex
    re_iter = re.finditer(r'((?:^|\s)\"|\"(?:\s|$))', message.content)

    indices = [m.start(0) for m in re_iter]
    content = list(message.content)

    if len(indices) == 1:
        indices = []

    else:

        rem_values = []

        # true represents an ending ", False represents a starting "
        temp_indices = [True if content[index] == '"' else False for index in indices]

        for index, value in enumerate(temp_indices[:-1]):

            if not value:
                indices[index] += 1
                if not temp_indices[index + 1]:
                    rem_values.append(index + 1)

            elif temp_indices[index + 1] and value:
                rem_values.append(index)

        for remove_index in rem_values:
            indices[remove_index] = 0

    # fear my list comprehension
    escaped_content = [r'\\"' if char == '"' and index not in indices else char for index, char in enumerate(content)]

    # reform list into a string
    message.content = "".join(escaped_content)

    return message


async def slash_send_embed(ctx, embeds, view=None, interaction=False):
    """
    A small bridging function to send embeds to a slash, view, normal command, or interaction

    Args:
        ctx: the context
        embeds: the embeds to send
        view: the view to send the embeds with
        interaction: whether or not the embeds are being sent to an interaction

    Returns:
        The message sent
    """
    try:
        embeds[0]
    except:
        embeds = [embeds]

    if isinstance(ctx, discord.Message):
        if view is not None:
            return await ctx.channel.send(embeds=embeds, view=view)
        else:
            return await ctx.channel.send(embeds=embeds)
    if isinstance(ctx, discord.ApplicationContext):
        if view is not None:
            return await ctx.respond(embeds=embeds, view=view)
        else:
            return await ctx.respond(embeds=embeds)
    elif interaction:
        if view is not None:
            return await ctx.response.send_message(embeds=embeds, view=view)
        else:
            return await ctx.response.send_message(embeds=embeds)
    else:
        if view is not None:
            return await ctx.send(embeds=embeds, view=view)
        else:
            return await ctx.send(embeds=embeds)


async def retrieve_shard(client, shard_id):
    """
    Retrieves the current shard name. Fallback to current shard id if no name is available

    Args:
        client: the client
        shard_id: the shard id

    Returns:
        The shard name if available, else the shard id
    """
    if shard_id > len(client.config["shard_names"]):
        return shard_id

    return client.config["shard_names"][shard_id]


def time_until_end_of_day():
    """
    a string representing the time until the end of the day for the bot's status.
    this is one of the oldest surviving functions from the old bot.

    Returns:
        The time until the end of the day in hours, minutes
    """
    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    a = datetime.datetime.combine(tomorrow, datetime.time.min) - datetime.datetime.utcnow()
    hours, remainder = divmod(int(a.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = ''
    if hours == 1:
        fmt += '{h} hour, '
    else:
        fmt += '{h} hours, '
    if minutes == 1:
        fmt += '{m} minute'
    else:
        fmt += '{m} minutes'
    return fmt.format(h=hours, m=minutes)


async def mention_string(client, prompt=""):
    """
    A function to compile a mention string for the bot

    Args:
        client: the client
        prompt: the prompt to use

    Returns:
        The mention string (@STW Daily prompt)
    """
    me = client.user
    try:
        return f"{me.mention} {prompt}"
    except AttributeError:
        # this is a fallback for when the bot is not ready, i guess
        # could probably make this an f string /shrug
        return "Mention me and then type {prompt} after!"


async def add_requested_footer(ctx, embed):
    """
    Adds the requested by user to the footer of the embed

    Args:
        ctx: the context
        embed: the embed to add the footer to

    Returns:
        The embed with the footer added
    """
    try:
        embed.set_footer(text=
                         f"\nRequested by: {ctx.author.name}"
                         , icon_url=ctx.author.display_avatar.url)
    except:
        embed.set_footer(text=
                         f"\nRequested by: {ctx.user.name}"
                         , icon_url=ctx.user.display_avatar.url)

    embed.timestamp = datetime.datetime.now()

    return embed


async def add_emoji_title(client, title, emoji):
    """
    Adds emojis surrounding the title of an embed

    Args:
        client: the client
        title: the title to add the emojis to
        emoji: the emoji to add

    Returns:
        The title with the emojis added
    """
    try:
        emoji = client.config["emojis"][emoji]
    except KeyError:
        emoji = client.config["emojis"]["placeholder"]
    return f"{emoji}  {title}  {emoji}"


async def split_emoji_title(client, title, emoji_1, emoji_2):
    """
    Adds two separate emojis surrounding the title of an embed

    Args:
        client: the client
        title: the title to add the emojis to
        emoji_1: the first emoji to add
        emoji_2: the last emoji to add

    Returns:
        The title with the emojis added
    """
    emoji_1 = client.config["emojis"][emoji_1]
    emoji_2 = client.config["emojis"][emoji_2]
    return f"{emoji_1}  {title}  {emoji_2}"


async def set_thumbnail(client, embed, thumb_type):
    """
    sets the thunbnail of an embed from the config key

    Args:
        client: the client
        embed: the embed
        thumb_type: the key of the thumbnail to set

    Returns:
        the embed with the thumbnail set
    """
    try:
        embed.set_thumbnail(url=client.config["thumbnails"][thumb_type])
    except KeyError:
        embed.set_thumbnail(url=client.config["thumbnails"]["placeholder"])
    return embed


def get_reward(client, day, vbucks=True):
    """
    gets the reward for the given day, accounting for non founders

    Args:
        client: the client
        day: the day to get the reward for
        vbucks: whether to get vbucks or not

    Returns:
        the reward for the given day and emoji key
    """
    day_mod = int(day) % 336
    if day_mod == 0:
        day_mod = 336

    item = items.ItemDictionary[str(day_mod)]
    emojis = item[1:]

    if not vbucks:
        try:
            item = [item[0].replace('V-Bucks & ', '')]
            emojis[emojis.index('mtxswap_combined')] = 'xray'
        except:
            pass

    emoji_text = ""
    for emoji in emojis:
        emoji_text += client.config["emojis"][emoji]

    return [item[0], emoji_text]


def get_bb_reward_data(client, response=None, error=False, pre_calc_day=0):
    """
    gets the reward data for battle breakers rewards

    Args:
        client: the client
        response: the epic api response to get the data from
        error: whether there was an error or not
        pre_calc_day: the day to calculate the reward for

    Returns:
        the reward day, name, emoji key, description, quantity
    """
    if error:
        day = int(response['messageVars'][0]) - 1  # hello world explorer hi
    elif pre_calc_day > 0:  # do u see me minimizing it no
        day = pre_calc_day
    else:
        day = response["profileChanges"][0]["profile"]["stats"]["attributes"]["login_reward"]["next_level"] - 1

    # im not sure if it actually loops after day 1800, but just in case not like anyone will use this command anyway
    day_mod = int(day) % 1800
    if day_mod == 0:
        day_mod = 1800

    # done FORTIFICAITION OF THE NIGHT hmm i see folders
    asset_path_name = LoginRewards[0]["Rows"][str(day_mod)]["ItemDefinition"]["AssetPathName"]
    quantity = LoginRewards[0]['Rows'][str(day_mod)]['ItemCount']

    emoji, name, description = ext.battlebreakers.BBLootTable.BBLootTable[asset_path_name]

    emoji_text = client.config["emojis"][emoji]

    return [day, name, emoji_text, description, quantity]


def get_game_headers(game):
    """
    gets the http auth headers for the given game/context
    Args:
        game: bb, ios, fn pc client

    Returns:
        the headers
    """
    if game == "bb":
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic M2NmNzhjZDNiMDBiNDM5YTg3NTVhODc4YjE2MGM3YWQ6YjM4M2UwZjQtZjBjYy00ZDE0LTk5ZTMtODEzYzMzZmMxZTlk="
        }
    elif game == "ios":
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="
        }
    else:
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
        }
    return h


async def get_token(client, auth_code: str, game="fn"):
    """
    gets an access token for the given game/context
    Args:
        client: the client
        auth_code: the auth code to get the token for
        game: bb, ios, fn pc client

    Returns:
        the access token response
    """
    h = get_game_headers(game)
    d = {
        "grant_type": "authorization_code",
        "code": auth_code
    }
    url = client.config["endpoints"]["token"]

    return await client.stw_session.post(url, headers=h, data=d)


# hi
async def exchange_games(client, auth_token, game="fn"):
    """
    exchanges the given auth token for the given game
    Args:
        client: the client
        auth_token: the auth token to exchange
        game: the game to exchange for
    Returns:
        the new auth token response
    """
    h = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {auth_token}"
    }
    url = client.config["endpoints"]["exchange"]
    response = await client.stw_session.get(url, headers=h)

    exchange_json = orjson.loads(await response.read())
    exchange_code = exchange_json["code"]

    h = get_game_headers(game)
    d = {
        "grant_type": "exchange_code",
        "exchange_code": exchange_code
    }
    url = client.config["endpoints"]["token"]

    return await client.stw_session.post(url, headers=h, data=d)


async def processing_embed(client, ctx, title="Logging in and Processing", description="This won\'t take long..."):
    """
    Constructs the processing embed

    Args:
        client: the client
        ctx: the context
        title: the title of the embed
        description: the description of the embed

    Returns:
        the processing embed
    """
    colour = client.colours["success_green"]

    embed = discord.Embed(title=await add_emoji_title(client, f"{title}", "processing"),
                          description=f"```{description}```", colour=colour)
    embed = await add_requested_footer(ctx, embed)
    return embed


def random_error(client):
    """
    Gets a random error message

    Args:
        client: the client

    Returns:
        the randomly chosen error message
    """
    return random.choice(client.config["error_messages"])


async def check_for_auth_errors(client, request, ctx, message, command, auth_code, invite_link,
                                send_error_message=True):
    """
    Checks for auth errors and sends the appropriate message

    Args:
        client: the client
        request: the request to check
        ctx: the context
        message: the message to edit
        command: the command that was run
        auth_code: the auth code used
        invite_link: the support server invite link
        send_error_message: whether to send the error message or not

    Returns:
        If there was no error, returns True, access token, account id
        If there was an error, returns False, None, None
    """
    try:
        return True, request["access_token"], request["account_id"]
    except:
        error_code = request["errorCode"]

    error_colour = client.colours["error_red"]

    print(f'[ERROR]: {error_code}')
    # TODO: refactor text
    if error_code == 'errors.com.epicgames.account.oauth.authorization_code_not_found':
        # login error
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to authenticate with authcode:\n"
                         f"```{auth_code}```\n"
                         f"**This authcode is invalid, there are a few reasons why this can happen such as:**\n"
                         f"⦾ Your authcode has expired, you need to enter your authcode into the auth command within about a minute after getting it.\n"
                         f"⦾ You got the wrong type of authcode, such as the one from the url instead of the one from the body of the page\n"
                         f"\u200b\n"
                         f"You'll need to get a new auth code, you can get one by:\n"
                         f"[Refreshing the page to get a new code or by clicking here]({client.config['login_links']['login_fortntite_pc']})\n"
                         f"\u200b\n"),
            colour=error_colour
        )

    elif error_code == 'errors.com.epicgames.account.oauth.authorization_code_not_for_your_client':
        # invalid grant error
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to authenticate with authcode:\n"
                         f"```{auth_code}```\n"
                         f"This authorisation code is invalid because it was created with the wrong link.\n"
                         f"[You'll need to get a new authcode using this link](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({invite_link})\n"),
            colour=error_colour)

    elif error_code == 'errors.com.epicgames.accountportal.date_of_birth_verification_required':
        # invalid grant error
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to authenticate with authcode:\n"
                         f"```{auth_code}```\n"
                         f"Your account date of birth needs to be verified.\n"
                         f"Please launch Fortnite or login to [Epic Games](https://www.epicgames.com/fortnite) and try again.\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({invite_link})\n"),
            colour=error_colour)

    elif len(error_code) == 32:
        # login error
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to authenticate with authcode:\n"
                         f"```{auth_code}```\n"
                         f"**This authcode is invalid because this account does not own Fortnite: Save The World**\n"
                         f"⦾ You need STW to claim your any rewards, Note: you can only get V-Bucks if you own a __Founders Pack__ which is no longer available.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({invite_link})\n"),
            colour=error_colour
        )

    else:
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to authenticate with:\n"
                         f"```{auth_code}```\n"
                         f"Unknown reason for not being able to authenticate please try again, error received from epic:\n"
                         f"```{error_code}```\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({invite_link})\n"),
            colour=error_colour
        )

    embed = await set_thumbnail(client, embed, "error")
    embed = await add_requested_footer(ctx, embed)

    if send_error_message:
        await slash_edit_original(ctx, message, embed)
    else:
        return embed

    return False, None, None


async def slash_edit_original(ctx, msg, embeds, view=None, file=None):
    """
    Edits the original message sent by the bot

    Args:
        ctx: The context of the command
        msg: The message to edit
        embeds: The embeds to edit the message with
        view: The view to edit the message with
        file: The file to add to the message

    Returns:
        The edited message
    """
    try:
        embeds[0]
    except:
        embeds = [embeds]

    if isinstance(ctx, discord.ApplicationContext):
        if view is not None and file is not None:
            return await msg.edit_original_response(embeds=embeds, view=view, file=file)
        if view is not None:
            return await msg.edit_original_response(embeds=embeds, view=view)
        if file is not None:
            return await msg.edit_original_response(embeds=embeds, file=file)
        else:
            return await msg.edit_original_response(embeds=embeds)
    else:
        if view is not None and file is not None:
            return await msg.edit(embeds=embeds, view=view, file=file)
        if view is not None:
            return await msg.edit(embeds=embeds, view=view)
        if file is not None:
            return await msg.edit(embeds=embeds, file=file)
        else:
            return await msg.edit(embeds=embeds)


async def device_auth_request(client, account_id, token):
    """
    Sends a device auth request to epic

    Args:
        client: The client to use
        account_id: The account id to use
        token: The token to use
    """
    url = client.config["endpoints"]["device_auth"].format(account_id)
    header = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }

    return await client.stw_session.post(url, headers=header, json="")


async def profile_request(client, req_type, auth_entry, data="{}", json=None, profile_id="stw", game="fn",
                          profile_type="profile0"):
    """
    Request a profile from epic api
    Args:
        client: The client
        req_type: The type of profile related request to make
        auth_entry: The auth entry to use
        data: The data to send with the request
        json: The json to send with the request
        profile_id: The profile id to use in the request
        game: The game to use in the request
        profile_type: The profile type to use in the request

    Returns:
        The response from the request
    """
    if game == "bb":
        token = auth_entry["bb_token"]
        url = client.config["endpoints"]["bb_profile"].format(auth_entry["account_id"],
                                                              client.config["profile"][req_type], profile_type)
    else:
        token = auth_entry["token"]
        url = client.config["endpoints"]["profile"].format(auth_entry["account_id"], client.config["profile"][req_type],
                                                           client.config["profileid"][profile_id])
    header = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }

    if json is None:
        return await client.stw_session.post(url, headers=header, data=data)
    else:
        return await client.stw_session.post(url, headers=header, json=json)


async def shop_request(client, token):
    """
    Makes a request to the shop endpoint

    Args:
        client: discord client
        token: The auth token to use

    Returns:
        json response from the endpoint
    """

    h = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }

    async with client.stw_session.get(client.config["endpoints"]["store"], headers=h) as resp:
        return orjson.loads(await resp.read())


async def get_llama_store(shop):
    """
    Gets the llama store from the shop request

    Args:
        shop: The shop request

    Returns:
        The llama store
    """
    for store in shop["storefronts"]:
        if store["name"] == "CardPackStorePreroll":
            return store
    return None


async def free_llama_count(store):
    """
    Gets the amount of free llamas in the store, and any related info if available

    Args:
        store: The llama store from the shop query

    Returns:
        The amount of free llamas
    """
    free_llamas = []
    for entry in store["catalogEntries"]:
        if "Always" not in entry["devName"] and entry["prices"][0]["finalPrice"] == 0:
            free_llamas.append(entry)
    return len(free_llamas), free_llamas


async def claim_free_llamas(client, auth_entry, store, prerolled_offers):
    """
    Claims the free llamas in the store

    Args:
        client: The client
        auth_entry: The auth entry to use
        store: The llama store from the shop query
        prerolled_offers: The response to the populate prerolled offers request

    Returns:
        The response from the request
    """
    already_opened_free_llamas = 0
    free_llamas_count, free_llamas_list = await free_llama_count(store)
    if not free_llamas_count:
        return None
    else:
        items_from_llamas = []
        opened_llamas = 0
        for llama in free_llamas_list:
            llama_to_claim_offer_id = llama['offerId']
            try:
                llama_to_claim_title = llama['title']
            except:
                llama_to_claim_title = []
            llama_to_claim_template_id = llama['itemGrants'][0]['templateId']
            while True:
                req_populate_llamas = prerolled_offers  # llamas
                llama_tier = []
                for key in req_populate_llamas['profileChanges'][0]['profile']['items']:
                    if req_populate_llamas['profileChanges'][0]['profile']['items'][key]['templateId'].lower().startswith("prerolldata") and req_populate_llamas['profileChanges'][0]['profile']['items'][key]['attributes']['offerId'] == llama_to_claim_offer_id:
                        try:
                            llama_tier = req_populate_llamas['profileChanges'][0]['profile']['items'][key]['attributes']['highest_rarity']
                        except:
                            llama_tier = 0
                json = {"offerId": llama_to_claim_offer_id,
                        "purchaseQuantity": 1,
                        "currency": "GameItem",
                        "currencySubType": "AccountResource:currency_xrayllama",
                        "expectedTotalPrice": 0,
                        "gameContext": ""}
                req_buy_free_llama = await profile_request(client, "purchase", auth_entry, json=json,
                                                           profile_id="common_core")
                req_buy_free_llama_json = orjson.loads(await req_buy_free_llama.read())
                if "errorMessage" in req_buy_free_llama_json:
                    if "limit of" in req_buy_free_llama_json['errorMessage']:
                        if opened_llamas == 0:
                            already_opened_free_llamas += 1
                    if "because fulfillment" in req_buy_free_llama_json['errorMessage']:
                        "account is unable to claim free llama"
                    break
                else:
                    "opening llama_to_claim_name tier llama_tier"
                    llama_loot = req_buy_free_llama_json['notifications'][0]['lootResult']['items']
                    llama_loot_count = 0
                    opened_llamas += 1
                    for key in llama_loot:
                        template_id = key['itemType']
                        item_guid = key['itemGuid']
                        item_quantity = key['quantity']
                        item_name = template_id
                        try:
                            item_rarity = 'rarity'
                            item_type = 'type'
                        except:
                            item_rarity = "Unknown rarity"
                            item_type = "Unknown type"
                        llama_loot_count += 1
                        if item_rarity in ("common", "uncommon", "rare", "epic"):
                            items_from_llamas.append(
                                {"itemName": item_name, "itemType": item_type, "templateId": template_id,
                                 "itemGuid": item_guid, "itemRarity": item_rarity, "itemQuantity": item_quantity})
                        print(f"{llama_loot_count}: {item_rarity} | {item_type}: {item_quantity}x {item_name}")
        if int(already_opened_free_llamas) == free_llamas_count:
            "alreadyclaimed"
        else:
            if opened_llamas > 0:
                "successfully opened opened_llamas"


async def recycle_free_llama_loot(client, auth_entry, items_from_llamas, already_opened_free_llamas, free_llamas_count,
                                  recycle_config=None):
    """
    Recycles the free llama loot

    Args:
        client: The client
        auth_entry: The auth entry to use
        items_from_llamas: The items from the free llama loot
        already_opened_free_llamas: The amount of free llamas already opened
        free_llamas_count: The amount of free llamas
        recycle_config: The config for what to recycle

    Returns:
        The response from the request
    """

    if recycle_config is None:
        recycle_config = {'weapon': [''], 'trap': [''], 'survivor': [''], 'defender': [''], 'hero': ['']}
    rarities = {"off": "",
                "common": "common",
                "uncommon": "common, uncommon",
                "rare": "common, uncommon, rare",
                "epic": "common, uncommon, rare, epic"
                }
    item_rarities = {
        "weapon": rarities["off".lower()].split(", "),
        "trap": rarities["off".lower()].split(", "),
        "survivor": rarities["off".lower()].split(", "),
        "defender": rarities["off".lower()].split(", "),
        "hero": rarities["off".lower()].split(", ")
    }
    resources_message = ""

    tracked_resources = ["AccountResource:heroxp", "AccountResource:personnelxp", "AccountResource:phoenixxp",
                         "AccountResource:phoenixxp_reward", "AccountResource:reagent_alteration_ele_fire",
                         "AccountResource:reagent_alteration_ele_nature",
                         "AccountResource:reagent_alteration_ele_water",
                         "AccountResource:reagent_alteration_gameplay_generic",
                         "AccountResource:reagent_alteration_generic", "AccountResource:reagent_alteration_upgrade_r",
                         "AccountResource:reagent_alteration_upgrade_sr",
                         "AccountResource:reagent_alteration_upgrade_uc",
                         "AccountResource:reagent_alteration_upgrade_vr", "AccountResource:reagent_c_t01",
                         "AccountResource:reagent_c_t02", "AccountResource:reagent_c_t03",
                         "AccountResource:reagent_c_t04", "AccountResource:reagent_evolverarity_r",
                         "AccountResource:reagent_evolverarity_sr", "AccountResource:reagent_evolverarity_vr",
                         "AccountResource:reagent_people", "AccountResource:reagent_promotion_heroes",
                         "AccountResource:reagent_promotion_survivors", "AccountResource:reagent_promotion_traps",
                         "AccountResource:reagent_promotion_weapons", "AccountResource:reagent_traps",
                         "AccountResource:reagent_weapons", "AccountResource:schematicxp"]

    if int(already_opened_free_llamas) != free_llamas_count:
        items_to_recycle = []
        item_guids_to_recycle = []
        recycle_resources = []
        recycled_items_count = 0
        recycle_resources_count = 0
        for item in items_from_llamas:
            item_type = item['itemType']
            item_rarity = item['itemRarity']
            item_guid = item['itemGuid']
            try:
                if item_rarity in item_rarities[item_type]:
                    item_guids_to_recycle.append(item_guid)
                    items_to_recycle.append(item)
            except:
                pass
        if len(item_guids_to_recycle) != 0:
            # free llamas
            # Recycling and retiring selected items from opened_llamas free llamas...
            req_get_resources = await profile_request(client, "query", auth_entry)
            req_get_resources_json = orjson.loads(await req_get_resources.read())
            for resource in tracked_resources:
                for item in req_get_resources_json['profileChanges'][0]['profile']['items']:
                    if req_get_resources_json['profileChanges'][0]['profile']['items'][item]['templateId'] == resource:
                        recycle_resources.append({"itemGuid": item,
                                                  "templateId": resource,
                                                  "quantity": req_get_resources_json['profileChanges'][0]['profile']['items'][item]['quantity']
                                                  })
            json = {"targetItemIds": item_guids_to_recycle}
            recycle_request = await profile_request(client, "batch_recycle", auth_entry, json=json)
            recycle_request_json = orjson.loads(await recycle_request.read())
            req_get_resources2 = await profile_request(client, "query", auth_entry)
            req_get_resources2_json = orjson.loads(await req_get_resources2.read())
            # resources receive
            for resource in recycle_resources:
                resource_quantity = int(
                    req_get_resources2_json['profileChanges'][0]['profile']['items'][resource['itemGuid']]['quantity']) - int(resource['quantity'])
                if resource_quantity > 0:
                    recycle_resources_count += 1
                    resources_message += f"{recycle_resources_count}: {resource_quantity}x {resource['itemName']}. " \
                                        f"Total ammount: {req_get_resources2_json['profileChanges'][0]['profile']['items'][resource['itemGuid']]['quantity']}\n"
            print(resources_message)


async def validate_existing_session(client, token):
    """
    Validates an existing session

    Args:
        client: The client
        token: The token to validate

    Returns:
        The response from the request
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }
    endpoint = client.config["endpoints"]["verify"]
    valid = await client.stw_session.get(endpoint, headers=header, data="{}")
    # returns code 200 if valid, 401 if invalid
    if valid.status == 200:
        return True
    return False


def vbucks_query_check(profile_text):
    """
    Checks if the profile can claim vbucks or not

    This takes approximately 0.00016141ms to execute on a 1mb profile

    Args:
        profile_text: text of the target profile json

    Returns:
        True if the profile can claim vbucks, False if not
    """
    if 'Token:receivemtxcurrency' in profile_text:
        return True
    return False


async def auto_stab_stab_session(client, author_id, expiry_time):
    """
    Automatically logs out the user and clears data after a set amount of time

    Args:
        client: the client
        author_id: the id of the user
        expiry_time: the time to wait before logging out

    Returns:
        None
    """
    patience_is_a_virtue = expiry_time - time.time()
    await asyncio.sleep(patience_is_a_virtue)
    await manslaughter_session(client, author_id, expiry_time)
    return


async def manslaughter_session(client, account_id, kill_stamp):
    """
    Logs out the user and clears data

    Args:
        client: the client
        account_id: the id of the user to clear
        kill_stamp: the time the user was logged out

    Returns:
        True if the user was logged out, False if not
    """
    try:
        info = client.temp_auth[account_id]
        if kill_stamp == "override" or info['expiry'] == kill_stamp:
            client.temp_auth.pop(account_id, None)

            header = {
                "Content-Type": "application/json",
                "Authorization": f"bearer {info['token']}"
            }
            endpoint = client.config["endpoints"]["kill_token"].format(info['token'])
            await client.stw_session.delete(endpoint, headers=header, data="{}")
            return True
    except:
        return False
        # 😳 they will know 😳
        # now they know :D


async def entry_profile_req(client, entry, game):
    """
    Gets the profile of the user for an auth session entry

    Args:
        client: The client
        entry: The auth session entry
        game: The game to get the profile for

    Returns:
        The entry of the user
    """
    profile = await profile_request(client, "query", entry, game=game)
    profile_json = orjson.loads(await profile.read())

    if game == "fn":
        vbucks = await asyncio.gather(asyncio.to_thread(vbucks_query_check, await profile.text()))
        others = await asyncio.gather(asyncio.to_thread(json_query_check, profile_json))
        if others[0] is not None:
            entry["day"] = others[0]
        if not vbucks[0]:
            entry["vbucks"] = False

    if game == "bb":
        others = await asyncio.gather(asyncio.to_thread(bb_day_query_check, profile_json))
        if others[0] is not None:
            entry["bb_day"] = others[0] - 1

    return entry


async def add_other_game_entry(client, user_id, entry, game, other_games):
    """
    Adds an entry for another game to the user's auth session
    
    Args:
        client: The client
        user_id: The id of the user
        entry: The entry to add to
        game: The game to add the entry for
        other_games: The other games to add an entry for
    """
    token = entry[client.config["entry_token_key_for_game"][game]]

    for other_game in other_games:
        exchange = await exchange_games(client, token, other_game)
        exchange_json = orjson.loads(await exchange.read())
        new_token = exchange_json["access_token"]

        entry[client.config["entry_token_key_for_game"][other_game]] = new_token

        entry["games"].append(other_game)
        entry = await entry_profile_req(client, entry, other_game)
        # This should definitely return the entry so we can allow opt-out
        # forget above comment ig
    return entry


async def add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, bb_token=None, game="fn"):
    """
    Adds a temporary authentication session entry for the user

    Args:
        client: The client
        ctx: The context
        auth_token: The fortnite access token to store
        account_id: The epic account id
        response: The response (to grab displayname)
        add_entry: Whether to start or opt out of an auth session
        bb_token: The battlebreakers access token to store
        game: The game to add the entry for

    Returns:
        The authentication session entry of the user
    """
    display_name = response["displayName"]

    entry = {
        "token": auth_token,
        "account_id": account_id,
        "vbucks": True,
        "account_name": f"{display_name}",
        'expiry': time.time() + client.config["auth_expire_time"],
        "day": None,
        "bb_token": bb_token,
        "bb_day": None,
        "games": [game],
    }
    if add_entry:
        asyncio.get_event_loop().create_task(auto_stab_stab_session(client, ctx.author.id, entry['expiry']))

    entry = await entry_profile_req(client, entry, game)
    other_games = list(client.config["entry_token_key_for_game"].keys())
    other_games.remove(game)
    entry = await add_other_game_entry(client, ctx.author.id, entry, game, other_games)

    if add_entry:
        client.temp_auth[ctx.author.id] = entry

    return entry


def json_query_check(profile_text):
    """
    Checks if the profile has a days logged in value

    This takes approximately 0.0002796ms to execute on a 1mb profile

    Args:
        profile_text: The profile json object

    Returns:
        The days logged in value if it exists, None if not
    """
    try:
        return profile_text["profileChanges"][0]["profile"]["stats"]["attributes"]["daily_rewards"]["totalDaysLoggedIn"]
    except:
        return None


def bb_day_query_check(profile_text):
    """
    Checks if the profile has a next login reward level value

    Args:
        profile_text: The profile json object

    Returns:
        The day for tomorrows reward if it exists, None if not
    """
    try:
        # ROOT.profileChanges[0].profile.stats.attributes.login_reward.next_level
        return profile_text["profileChanges"][0]["profile"]["stats"]["attributes"]["login_reward"]["next_level"]
    except:
        return None


def extract_profile_item(profile_json, item_string="Currency:Mtx"):
    """
    Extracts an item from the profile json

    This takes approximately 0.13383596ms to execute on a 1mb profile

    Args:
        profile_json: The profile json object
        item_string: The item to extract

    Returns:
        A dictionary of found items
    """
    found_items = {}
    num = 0
    try:
        for attribute, value in profile_json["profileChanges"][0]["profile"]["items"].items():
            if item_string in value["templateId"]:
                found_items.update({num: value})
                num += 1
    except:
        pass
    return found_items


async def get_stw_news(client):
    """
    Gets the news for stw from epic games

    Args:
        client: The client

    Returns:
        The news for stw from epic games
    """
    endpoint = client.config["endpoints"]["stw_news"]
    return await client.stw_session.get(endpoint)


async def get_br_news(client):
    """
    Gets the news for br from fortnite-api as its personalised from epic games

    Args:
        client: The client

    Returns:
        The news for br from fortnite-api
    """
    # TODO: This should be changed to use the epic games api
    # We can't use the epic games api as it requires a personalised request
    endpoint = client.config["endpoints"]["br_news"]
    return await client.stw_session.get(endpoint)


async def create_news_page(self, ctx, news_json, current, total):
    """
    Creates a news page embed

    Args:
        self: The client
        ctx: The context
        news_json: The news json
        current: The current page
        total: The total pages

    Returns:
        the constructed news embed
    """
    generic = self.client.colours["generic_blue"]
    embed = discord.Embed(title=await add_emoji_title(self.client, "News", "bang"),
                          description=f"\u200b\n**News page {current} of {total}:**\u200b\n"
                                      f"**{news_json[current - 1]['title']}**"
                                      f"\n{news_json[current - 1]['body']}",
                          colour=generic)

    embed.description += "\u200b\n\u200b"

    # set embed image
    embed = await set_embed_image(embed, news_json[current - 1]["image"])
    embed = await set_thumbnail(self.client, embed, "newspaper")
    embed = await add_requested_footer(ctx, embed)
    return embed


async def set_embed_image(embed, image_url):
    """
    Sets the embed image

    Args:
        embed: The embed to set the image for
        image_url: The image url to set

    Returns:
        The embed with the image set
    """
    return embed.set_image(url=image_url)


async def resolve_vbuck_source(vbuck_source):
    """
    Resolves the vbuck source to a user friendly name and emoji

    Args:
        vbuck_source: The vbuck source

    Returns:
        The user friendly name, and emoji
    """
    if vbuck_source == "Currency:MtxGiveaway":
        return "Battle Pass", "bp_icon2"
    elif vbuck_source == "Currency:MtxComplimentary":
        return "Save the World", "library_cal"
    elif vbuck_source == "Currency:MtxPurchased":
        return "Purchased", "vbuck_icon"
    elif vbuck_source.lower() == "currency:mtxpurchasebonus":  # idk the casing for this
        return "Purchase Bonus", "vbuck_icon"
    elif vbuck_source == "Currency:MtxDebt":
        return "Debt", "LMAO"
    else:
        return vbuck_source, "placeholder"


async def calculate_vbucks(item):
    """
    Calculates the total vbucks from a dict of items

    Args:
        item: The dict of items

    Returns:
        The total vbucks quantity
    """
    vbucks = 0
    if item:
        for item in item:
            for attr, val in item.items():
                if "debt" in val["templateId"].lower():
                    vbucks -= val["quantity"]
                else:
                    vbucks += val["quantity"]
    return vbucks


async def get_banner_colour(colour, colour_format="hex", colour_type="Primary"):
    """
    Gets the banner colour from the banner name

    Args:
        colour: The colour of the banner (e.g. DefaultColor1)
        colour_format: The format to return the colour in (hex, rgb)
        colour_type: The colour to fetch (Primary, Secondary)

    Returns:
        The banner colour in the specified format (default hex)
    """
    colour_key = BannerColors[0]["Rows"][colour]["ColorKeyName"]
    colour_map = BannerColorMap[0]["Properties"]["ColorMap"][colour_key][f"{colour_type}Color"]
    colour_hex = f'#{colour_map["Hex"][2:]}'
    if colour_format == "hex":
        return colour_hex
    elif colour_format == "rgb":
        return tuple(int(colour_hex[i:i + 2], 16) for i in (1, 3, 5))
    else:
        return None


def truncate(string, length=100, end="..."):
    """
    Truncates a string to a certain length

    Args:
        string: The string to truncate
        length: The length to truncate to
        end: The end of the string to use when truncated

    Returns:
        The truncated string
    """
    return (string[:length - 3] + end) if len(string) > length else string


def get_tomorrow_midnight_epoch():
    """
    Gets the epoch for tomorrow UTC midnight, independent of timezone

    Returns:
        The epoch for tomorrow UTC midnight in seconds
    """
    return int(time.time() + 86400 - time.time() % 86400)


def get_item_icon_emoji(client, template_id):
    """
    Gets the emoji for the item icon

    Args:
        client: The client
        template_id: The template id of the item

    Returns:
        The emoji for the item icon
    """
    try:
        try:
            filtered = re.split(r"[/:\s]|_t0", template_id)[1]
        except:
            filtered = template_id
        if 'bow' in filtered:
            return client.config['emojis']['bow']
        outcome = max(client.config['emojis'], key=lambda emoji: SequenceMatcher(a=emoji, b=filtered).ratio())
        similarity = SequenceMatcher(a=outcome, b=filtered).ratio()
        if similarity < 0.5:
            # if the first 5 characters match in outcome and filtered, then it's probably a match
            if outcome[:4] == filtered[:4]:
                pass
            else:
                outcome = 'placeholder'
        return client.config['emojis'][outcome]
    except:
        return client.config['emojis']['placeholder']


def llama_contents_render(client, llama_items):
    """
    Renders the contents of a llama

    Args:
        client: The client
        llama_items: The items in the llama

    Returns:
        The rendered contents of the llama
    """
    string = ""
    for item in llama_items:
        string += f" {get_item_icon_emoji(client, item['itemType'])} {'x' + str(item['quantity']) if item['quantity'] > 1 else ''}  "
    return string


def get_rating(data_table=SurvivorItemRating, row="Default_C_T01", time_input=0):
    """
    Calculates the power level of an item in stw

    Args:
        data_table: The data table to use
        row: The row to use
        time_input: The time input

    Returns:
        The power level of the item
    """
    row_data = data_table[0]['Rows'][row]
    # ROOT[0].Rows.Default_C_T01.Keys[0].Time
    # clamp to lower bound.
    if time_input < row_data['Keys'][0]['Time']:
        return row_data['Keys'][0]['Value']

    # clamp to upper bound.
    if time_input >= row_data['Keys'][-1]['Time']:
        return row_data['Keys'][-1]['Value']

    # find the two keys that the time_input is between.
    for i in range(len(row_data['Keys']) - 1):
        if row_data['Keys'][i]['Time'] <= time_input < row_data['Keys'][i + 1]['Time']:
            # interpolate between the two keys.
            return row_data['Keys'][i]['Value'] + (time_input - row_data['Keys'][i]['Time']) / (
                    row_data['Keys'][i + 1]['Time'] - row_data['Keys'][i]['Time']) * (
                    row_data['Keys'][i + 1]['Value'] - row_data['Keys'][i]['Value'])


def parse_survivor_template_id(template_id):
    """
    Parses the template id of a survivor

    Examples of template id's that may be passed:
    Worker:managerexplorer_sr_eagle_t05
    Worker:workerbasic_sr_t05;
    Worker:worker_halloween_smasher_sr_t05
    Worker:worker_joel_ur_t05

    Args:
        template_id: The template id to parse

    Returns:
        The type of survivor (e.g. worker, manager, basic), The tier of survivor (e.g. t01, t02, t03, t04, t05), The rarity of survivor (e.g. c, uc, r, vr, sr, ur), The name of the survivor if available (e.g. eagle, smasher, joel)
    """
    tid = template_id.split(":")[1]
    fields = tid.split("_")

    if fields[0] == "worker":
        survivor_type = "special"
        fields.pop(0)
    elif "manager" in fields[0]:
        survivor_type = "manager"
        fields[0] = fields[0].split("manager")[1]
    else:
        survivor_type = "basic"
        fields.pop(0)

    tier = fields.pop(-1)

    if "halloween" in fields[0]:
        fields.pop(0)

    if len(fields) == 1:
        rarity = fields.pop(0)
    else:
        rarity = fields.pop(1)

    # if survivor_type == "manager":
    #     rarity = fields.pop(-2)
    # else:
    #     rarity = fields.pop(-1)

    name = ""
    for val in fields:
        name += val + "_"

    return survivor_type, tier, rarity, name[:-1]


# print(parse_survivor_template_id("Worker:managerexplorer_sr_eagle_t05"))
# print(parse_survivor_template_id("Worker:workerbasic_sr_t05"))
# print(parse_survivor_template_id("Worker:worker_halloween_smasher_sr_t05"))
# print(parse_survivor_template_id("Worker:worker_joel_ur_t05"))

# print(get_rating(data_table=HomebaseRatingMapping, row="UIMonsterRating", time_input=52025))
# print(get_rating(data_table=SurvivorItemRating, row="Default_C_T01", time_input=50))

# leader = {
#     'templateId': 'Worker:managergadgeteer_sr_fixer_t05',
#     'attributes': {
#         'squad_id': 'squad_attribute_scavenging_gadgeteers',
#         'personality': 'Homebase.Worker.Personality.IsAnalytical',
#         'level': 50,
#         'squad_slot_idx': 0,
#         'item_seen': True,
#         'managerSynergy': 'Homebase.Manager.IsGadgeteer',
#         'portrait': 'WorkerPortrait:IconDef-ManagerPortrait-SR-Gadgeteer-fixer',
#         'favorite': True,
#         'building_slot_used': -1
#     },
#     'quantity': 1
# }
# worker = {
#     'templateId': 'Worker:workerbasic_sr_t05',
#     'attributes': {
#         'personality': 'Homebase.Worker.Personality.IsAnalytical',
#         'gender': '1',
#         'squad_id': 'squad_attribute_scavenging_gadgeteers',
#         'level': 50,
#         'squad_slot_idx': 5,
#         'item_seen': True,
#         'portrait': 'WorkerPortrait:IconDef-WorkerPortrait-Analytical-M03',
#         'building_slot_used': -1,
#         'set_bonus': 'Homebase.Worker.SetBonus.IsAbilityDamageLow'
#     },
#     'quantity': 1
# }


def get_survivor_rating(survivor):
    """
    Gets the power level of a survivor from a profile's survivor entry dict

    An example of a survivor dict:

    worker = {
        'templateId': 'Worker:workerbasic_sr_t05',

        'attributes': {
            'personality': 'Homebase.Worker.Personality.IsAnalytical',
            'gender': '1',
            'squad_id': 'squad_attribute_scavenging_gadgeteers',
            'level': 50,
            'squad_slot_idx': 5,
            'item_seen': True,
            'portrait': 'WorkerPortrait:IconDef-WorkerPortrait-Analytical-M03',
            'building_slot_used': -1,
            'set_bonus': 'Homebase.Worker.SetBonus.IsAbilityDamageLow'
        },

        'quantity': 1
        }

    Args:
        survivor: The survivor dict. This must have: templateId, attributes.level

    Returns:
        Tuple: (The power level of the survivor, (The type of survivor (e.g. worker, manager, basic), The tier of survivor (e.g. t01, t02, t03, t04, t05), The rarity of survivor (e.g. c, uc, r, vr, sr, ur), The name of the survivor if available (e.g. eagle, smasher, joel)))
    """
    survivor_info = parse_survivor_template_id(survivor["templateId"])
    if survivor_info[0] == "manager":
        survivor_type = "Manager"
    else:
        survivor_type = "Default"
    return get_rating(data_table=SurvivorItemRating,
                      row=f"{survivor_type}_{survivor_info[2].upper()}_{survivor_info[1].upper()}",
                      time_input=survivor["attributes"]["level"]), survivor_info


# print(get_survivor_rating(leader))
# print(get_survivor_rating(worker))

def get_survivor_bonus(leader_personality, survivor_personality, leader_rarity, survivor_rating):
    """
    Gets the bonus to the powerlevel of a survivor based on the leader's personality and rarity, and the survivor's personality and rating
    
    Args:
        leader_personality: The personality of the leader (e.g. Homebase.Worker.Personality.IsAnalytical)
        survivor_personality: The personality of the survivor (e.g. Homebase.Worker.Personality.IsAnalytical)
        leader_rarity: The rarity of the leader (e.g. c, uc, r, vr, sr, ur)
        survivor_rating: The power level of the survivor (e.g. 50)

    Returns:
        The bonus delta to the power level of the survivor (e.g. 8)
    """
    if leader_personality == survivor_personality:
        if leader_rarity == 'sr' or leader_rarity == 'ur':
            return 8
        if leader_rarity == 'vr':
            return 5
        if leader_rarity == 'r':
            return 4
        if leader_rarity == 'uc':
            return 3
        if leader_rarity == 'c':
            return 2

    elif leader_rarity == 'sr':
        if survivor_rating <= 2:
            return 0
        return -2

    return 0


def get_lead_bonus(lead_synergy, squad_name, rating):
    """
    Gets the bonus to the power level of a lead survivor based on the leader's synergy, squad and rating
    
    Args:
        lead_synergy: The synergy of the leader (e.g. Homebase.Manager.IsGadgeteer)
        squad_name: The name of the squad (e.g. squad_attribute_scavenging_gadgeteers)
        rating: The power level of the leader (e.g. 50)

    Returns:
        The lead's rating (to effectively double it) if applicable, otherwise 0, (to effectively do nothing)
    """
    # TODO: move this to a better location
    stw_lead_synergy = {
        "trainingteam": 'IsTrainer',
        "fireteamalpha": 'IsSoldier',
        "closeassaultsquad": 'IsMartialArtist',
        "thethinktank": 'IsInventor',
        "emtsquad": 'IsDoctor',
        "corpsofengineering": 'IsEngineer',
        "scoutingparty": 'IsExplorer',
        "gadgeteers": 'IsGadgeteer'
    }
    if stw_lead_synergy[squad_name] == lead_synergy:
        return rating
    return 0


def calculate_homebase_rating(profile):
    """
    Calculates the power level of a profile's homebase by calculating FORT stats

    Formula to calculate should be something like:

    1. FORT stat calculation
    - query (public) profile campaign
        - loop through items
            - templateId Worker:workerx_xx_xxx
                x - usually 'basic'; Halloween survivors are '_halloween_type'
                xx - rarity; vr - epic, sr - legendary, etc
                xxx - tier; t01-t05, evolution
            - templateId Worker:managerx_xx_xxx_xxxx
                x - leader synergy, doctor, martialartist, trainer etc
                xx - rarity; vr, sr
                xxx - portrait; treky, dragon, yoglattes etc
                xxxx - tier; t01-t05, evolution
        - get rarity, tier, level to calculate power level of survivor (use SurvivorItemRating.json)
            - row 	- Default_C_T01 -> Default_UR_T06
                    - Manager_C_T01 -> Manager_SR_T06
            - mapping appears to be a keys list with the input (time) being level, and output (value) being power level
                - ROOT[0].Rows.{type_rarity_tier}.Keys[point0].Time/Value //linear curve
        - leader job match bonus for each squad
            - (value doubled on correct squad)
        - follower personality match bonus
            - (increased/decreased with leader personality (amount depends on leader rarity))
        - fort stat bonus from research stats
            There are separate items for individual and team stats
    - add up and multiply by 4
    - use HomebaseRatingMapping.json to map value

    # TODO: Ventures stats
    ventures - same mapping, fort stats from phoenix stats

    Args:
        profile: The profile json to calculate the power level of

    Returns:
        The power level of the profile's homebase, total FORT stats, and dict of FORT stats by type
    """
    # ROOT.profileChanges[0].profile.items
    workers = extract_profile_item(profile, "Worker:")
    survivors = {}
    total_stats = {"fortitude": 0,
                   "offense": 0,
                   "resistance": 0,
                   "technology": 0}
    stw_role_map = {
        "IsTrainer": 'fortitude',
        "IsSoldier": 'offense',
        "IsMartialArtist": 'offense',
        "IsInventor": 'technology',
        "IsDoctor": 'fortitude',
        "IsEngineer": 'technology',
        "IsExplorer": 'resistance',
        "IsGadgeteer": 'resistance'
    }
    # organise into a dict
    for attr, val in workers.items():
        if val["attributes"]["squad_slot_idx"] == -1:
            continue

        # if val["attributes"]["squad_slot_idx"] == 0:
        #     survivors.update({"leader": val})
        # else:
        #     survivors.update({val["attributes"]["squad_slot_idx"]: val})
        # print(val)
        personality = val["attributes"]["personality"].split(".")[-1]
        squad = val["attributes"]["squad_id"]
        if squad == '':
            continue
        rating, info = get_survivor_rating(val)
        if info[0] == "manager":
            synergy = val["attributes"]["managerSynergy"]
            try:
                survivors[squad].update({f"Leader": [rating, info, personality, synergy]})
            except:
                survivors.update({squad: {f"Leader": [rating, info, personality, synergy]}})
        else:
            try:
                survivors[squad]["Followers"].update({f"Follower{attr}": [rating, info, personality]})
            except:
                survivors.update({squad: {"Followers": {f"Follower{attr}": [rating, info, personality]}}})
        # survivors.update()
        # print(rating, personality, squad)
    # print(survivors)
    # leader / survivor bonuses
    for attr, val in survivors.items():
        try:
            val["Leader"][0] += get_lead_bonus(val["Leader"][-1].split(".")[-1], attr.split("_")[-1], val["Leader"][0])
        except:
            pass
        for follower, stats in val["Followers"].items():
            try:
                stats[0] += get_survivor_bonus(val["Leader"][-2], stats[-1], val["Leader"][1][-2], stats[0])
            except:
                pass

    # research stats
    # ROOT.profileChanges[0].profile.stats.attributes.research_levels
    research_levels = extract_profile_item(profile, "Stat:")
    for attr, val in research_levels.items():
        if "_team" in val["templateId"]:
            if "phoenix" in val['templateId'].lower():
                continue
            total_stats[val['templateId'].split(':')[1].split("_")[0].lower()] += get_rating(data_table=ResearchSystem,
                                                                                             row=f"{val['templateId'].split(':')[1]}_cumulative",
                                                                                             time_input=val["quantity"])
        else:
            # exclude phoenix stats
            if "phoenix" in val['templateId'].lower():
                continue
            total_stats[val['templateId'].split(':')[1].lower()] += get_rating(data_table=ResearchSystem,
                                                                               row=f"{val['templateId'].split(':')[1]}_personal_cumulative",
                                                                               time_input=val["quantity"])
    # for attr, val in research_levels.items():
    #     total_stats += val
    for attr, val in survivors.items():
        try:
            total_stats[stw_role_map[val["Leader"][-1].split(".")[-1]]] += val["Leader"][0]
        except:
            continue
        for follower, stats in val["Followers"].items():
            try:
                total_stats[stw_role_map[val["Leader"][-1].split(".")[-1]]] += stats[0]
            except:
                continue

    # print(survivors)
    # print(workers)

    cmd_level = profile["profileChanges"][0]["profile"]["stats"]["attributes"]["level"]
    # print(cmd_level)
    # print(total_stats)
    for attr, val in AccountLevels[0]["Rows"].items():
        if int(attr) <= cmd_level:
            if val["Rewards"][0]["TemplateId"] == "Stat:fortitude":
                total_stats['fortitude'] += val["Rewards"][0]["Quantity"]
            if val["Rewards"][0]["TemplateId"] == "Stat:offense":
                total_stats['offense'] += val["Rewards"][0]["Quantity"]
            if val["Rewards"][0]["TemplateId"] == "Stat:resistance":
                total_stats['resistance'] += val["Rewards"][0]["Quantity"]
            if val["Rewards"][0]["TemplateId"] == "Stat:technology":
                total_stats['technology'] += val["Rewards"][0]["Quantity"]

    # combine total stats into one number
    total = 0
    for attr, val in total_stats.items():
        total_stats[attr] = int(val + 24)
        total += val + 24
    return get_rating(data_table=HomebaseRatingMapping, row="UIMonsterRating",
                      time_input=total * 4), total, total_stats


# alexanda  now who is she
async def get_or_create_auth_session(client, ctx, command, original_auth_code, add_entry=False, processing=True,
                                     dont_send_embeds=False):  # hi bye
    """
    I no longer understand this function, its ways of magic are beyond me, but to the best of my ability this is what it returns

    If an authcode is found in the system (aka for this user they are currently authenticated) then one of these two options will be selected:


    A Processing embed should be created:

                [ the message object of the processing ... embed,
                the existing authentication info,
                an empty list which represents no embeds or something?]

    A processing embed should not be created:

                [ None to represent the missing message object for the processing embed,
                The existing authentication information,
                another empty list to represent something]


    If existing authentication information is not found then it will attempt to detect any pre-epic game api request errors, basically input sanitization,
    if an error is found then it returns a list of [False], because obviously past me decided that was a good idea.

    Now if an error does not happen then it returns a list of:
    [ The message object of the processing ... embed,
    the authentication information,
    some sort of embed which represents the successful authentication]

    That hopefully covers everything,
    if you're reading this then say hello in the STW-Daily discord server general channel. ;D

    Args:
        client (discord.Client): The discord client object
        ctx (discord.ext.commands.Context): The context of the command
        command (str): The command that is being executed
        original_auth_code (str): The authcode that was provided by the user
        add_entry (bool, optional): Whether or not to add an entry to the database. Defaults to False.
        processing (bool, optional): Whether or not to create a processing embed. Defaults to True.
        dont_send_embeds: if this is true then it will not send the embeds, this is used for the device auth command

    Returns:
        If successfully created auth session, a list - [processing embed, auth info, success embed] <br></br> returns a list - [processing embed, existing auth entry, embed] if auth exists <br></br> returns a list - [False] if an error occurs
    """

    # extract auth code from auth_code
    extracted_auth_code = extract_auth_code(original_auth_code)
    embeds = []

    # Attempt to retrieve the existing auth code.
    try:
        existing_auth = client.temp_auth[ctx.author.id]
    except:
        existing_auth = None

    # Return auth code if it exists
    if existing_auth is not None and extracted_auth_code == "":

        # Send the logging in & processing if given
        if processing and not dont_send_embeds:
            proc_embed = await processing_embed(client, ctx)
            return [await slash_send_embed(ctx, proc_embed),
                    existing_auth,
                    embeds]

        return [None, existing_auth, embeds]

    error_colour = client.colours["error_red"]
    white_colour = client.colours["auth_white"]
    error_embed = None
    support_url = client.config["support_url"]

    auth_client_id = "ec684b8c687f479fadea3cb2ad83f5c6"

    # Basic checks so that we don't stab stab epic games so much
    if extracted_auth_code == "":
        error_embed = discord.Embed(title=await add_emoji_title(client, f"No Auth Code", "error"), description=(
            f"\u200b\n**You need an auth code, you can get one from:**\n"
            f"[Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D{auth_client_id}%2526responseType%253Dcode)\n"
            f"[Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId={auth_client_id}&responseType=code)\n\n"
            f"**Need Help? Run**\n"
            f"{await mention_string(client, 'help {0}'.format(command))}\n"
            f"Or [Join the support server]({support_url})\n"), colour=error_colour)

    elif extracted_auth_code in client.config["known_client_ids"]:
        error_embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to authenticate with authcode:\n"
                         f"```{extracted_auth_code}```\n"
                         f"**This authcode is from the URL & not from the body of the page:**\n"
                         f"⦾ The authcode you need is the one from the pages body, not the one from the url.\n"
                         f"\u200b\n"
                         f"If you need a new authcode you can get one by:\n"
                         f"[Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId={auth_client_id}&responseType=code)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )

    elif extracted_auth_code == "errors.stwdaily.illegal_auth_code" or (re.sub('[ -~]', '', extracted_auth_code)) != "":
        error_embed = discord.Embed(title=await add_emoji_title(client, random_error(client), "error"), description=(
            f"\u200b\n"
            f"Attempted to authenticate with authcode:\n"
            f"```{original_auth_code}```\n"
            f"Your auth code contains characters not present in auth codes. Please try copying your code again, or getting a new one\n\n"
            f"**An Example:**\n"
            f"```a51c1f4d35b1457c8e34a1f6026faa35```\n"
            f"If you need a new authcode you can get one by:\n"
            f"[Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId={auth_client_id}&responseType=code)\n"
            f"\u200b\n"
            f"**If you need any help try:**\n"
            f"{await mention_string(client, 'help {0}'.format(command))}\n"
            f"Or [Join the support server]({support_url})\n"),
                                    colour=error_colour)

    elif len(extracted_auth_code) != 32:
        error_embed = discord.Embed(title=await add_emoji_title(client, random_error(client), "error"), description=(
            f"\u200b\n"
            f"Attempted to authenticate with authcode:\n"
            f"```{extracted_auth_code}```\n"
            f"Your authcode should only be 32 characters long, and only contain numbers and letters. Check if you have any stray quotation marks\n\n"
            f"**An Example:**\n"
            f"```a51c1f4d35b1457c8e34a1f6026faa35```\n"
            f"If you need a new authcode you can get one by:\n"
            f"[Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId={auth_client_id}&responseType=code)\n"
            f"\u200b\n"
            f"**If you need any help try:**\n"
            f"{await mention_string(client, 'help {0}'.format(command))}\n"
            f"Or [Join the support server]({support_url})\n"),
                                    colour=error_colour)

    if error_embed is not None:
        embed = await set_thumbnail(client, error_embed, "error")
        embed = await add_requested_footer(ctx, embed)

        if not dont_send_embeds:
            await slash_send_embed(ctx, embed)
            return [False]
        else:
            return embed

    if not dont_send_embeds:
        proc_embed = await processing_embed(client, ctx)
        message = await slash_send_embed(ctx, proc_embed)
    else:
        message = None

    token_req = await get_token(client, extracted_auth_code)  # we auth for fn regardless of the game because exchange
    response = orjson.loads(await token_req.read())
    check_auth_error_result = await check_for_auth_errors(client, response, ctx, message, command,
                                                          extracted_auth_code, support_url, not dont_send_embeds)

    try:
        success, auth_token, account_id = check_auth_error_result
    except:
        return check_auth_error_result

    if not success:
        return [success]

    # # if authing for battle breakers
    # if game == "bb":
    #     # if session already exists
    #     try:
    #         # if existing fn session exists
    #         if client.temp_auth[ctx.author.id]["token"] is not None:
    #             entry = await add_temp_entry(client, ctx, client.temp_auth[ctx.author.id]["token"],
    #                                          account_id, response, add_entry, bb_token=auth_token, game=game)
    #         # no fn session, set fn token to none
    #         else:
    #             entry = await add_temp_entry(client, ctx, None, account_id, response, add_entry, bb_token=auth_token,
    #                                          game=game)
    #     # no session at all
    #     except:
    #         entry = await add_temp_entry(client, ctx, None, account_id, response, add_entry, bb_token=auth_token,
    #                                      game=game)
    # # if authing for fn
    # else:
    #     # if session already exists
    #     try:
    #         # if existing bb session exists
    #         if client.temp_auth[ctx.author.id]["bb_token"] is not None:
    #             entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry,
    #                                          bb_token=client.temp_auth[ctx.author.id]["bb_token"], game=game)
    #         # no bb session, set bb token to None
    #         else:
    #             entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, game=game)
    #     # no session at all (most common outcome of all this junk 🫠)
    #     except:
    #         entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, game=game)

    entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry)  # authing for fn first
    # print(entry)
    # print(game)
    # if game != "fn":
    #     print("bb")
    #     entry = await add_temp_entry(client, ctx, entry["token"], account_id, response, add_entry,
    #                                  bb_token=auth_token, game=game)  # now auth for desired game
    #     print(entry)

    embed = discord.Embed(title=await add_emoji_title(client, "Successfully Authenticated", "whitekey"),
                          description=f"```Welcome, {entry['account_name']}```\n", colour=white_colour)

    if add_entry:
        embed.description += f"{client.config['emojis']['stopwatch_anim']} Your session will expire <t:{math.floor(client.config['auth_expire_time'] + time.time())}:R>\n\u200b\n"
    else:
        embed.description += f"{client.config['emojis']['cross']} Did not start an auth session\n\u200b\n"

    if not entry['vbucks']:
        embed.description += f"• You'll receive {client.config['emojis']['xray']} X-Ray tickets instead of {client.config['emojis']['vbucks']} V-Bucks. [Learn more](https://github.com/dippyshere/stw-daily/wiki)\n\u200b"
    if not entry['vbucks'] and not entry['day']:
        embed.description += "\n"
    if not entry['day']:
        embed.description += f"• You don't have Save the World. [Learn more](https://github.com/dippyshere/stw-daily/wiki)\n\u200b"

    embed = await set_thumbnail(client, embed, "keycard")
    embed = await add_requested_footer(ctx, embed)

    embeds.append(embed)
    return [message, entry, embeds]


async def post_error_possibilities(ctx, client, command, acc_name, error_code, support_url, error_level="error",
                                   response=None):
    """
    Handle errors that could occur when posting to the api, and present an embed with possible solutions

    Args:
        ctx: The context of the command
        client: The client
        command: The command that was run
        acc_name: The account name of the user
        error_code: The error code that was returned
        support_url: The support server url
        error_level: The level of error, either error or warning
        response: The response from the api

    Returns:
        an error embed
    """
    error_colour = client.colours["error_red"]
    yellow = client.colours["warning_yellow"]

    # Epic Games Error Codes
    if error_code == "errors.com.epicgames.common.missing_action":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to claim daily because:**\n"
                         f"⦾ Your account has not yet opened Fortnite before\n"
                         f"⦾ Your account has been banned and therefore you cannot claim your daily rewards.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.fortnite.check_access_failed":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to claim daily because this account does not own Fortnite: Save The World:**\n"
                         f"⦾ You need STW to claim your any rewards, Note: you can only get V-Bucks if you own a __Founders Pack__ which is no longer available.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.common.authentication.token_verification_failed":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to claim daily because your token has expired**\n"
                         f"⦾ Please reauthenticate your account, you can get an auth code from:\n"
                         f"\n"
                         f"[Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)\n"
                         f"[Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.validation.validation_failed":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Uh oh! Ran into an error with STW Daily or Epic Games**\n"
                         f"⦾ Validation for a request has failed\n"
                         f"⦾ Please ask for support in the support server about this.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.accountportal.date_of_birth_verification_required":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to login with account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to login because your account needs to verify it's date of birth.**\n"
                         f"⦾ Please login on [Epic Games](https://www.epicgames.com/fortnite) to set your DOB and try again.\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )
    # battle breakers error codes
    elif error_code == "errors.com.epicgames.world_explorers.login_reward_not_available":
        reward = get_bb_reward_data(client, response, True)
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "warning"), description=
            (f"\u200b\n"
             f"You have already claimed your reward for day **{reward[0]}**.\n"
             f"\u200b\n"
             f"**{reward[2]} Todays reward was:**\n"
             f"```{reward[4]} {reward[1]}```\n"
             f"You can claim tomorrow's reward <t:{get_tomorrow_midnight_epoch()}:R>\n"
             f"\u200b\n"), colour=yellow)
        error_level = "warn"

    # STW Daily Error Codes
    elif error_code == "errors.stwdaily.failed_guid_research":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to find GUID for research item**\n"
                         f"⦾ Please ensure you have claimed research points at least once in-game\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.failed_get_collected_resource_item":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to get item from notifications using token_guid_research**\n"
                         f"⦾ Please ensure you have claimed research points at least once in-game\n"
                         f"⦾ If this continues please ask for support in the support server.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.failed_get_collected_resource_type":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to get collectedResourceResult type from notifications**\n"
                         f"⦾ Please ensure you have claimed research points at least once in-game\n"
                         f"⦾ If this continues please ask for support in the support server.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.failed_total_points":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Failed to find total research points item from query profile**\n"
                         f"⦾ You could be out of research points, please just wait a few seconds and re run the command.\n"
                         f"⦾ Please ensure you have claimed research points at least once in-game\n"
                         f"⦾ If this continues please ask for support in the support server.\n"
                         f"\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.not_author_interaction_response":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Not the author:```You need to be the author to utilise the {command} view!```\n"
                         f"**If you want to utilise this view, please use the command yourself.**\n"
                         f"\n"
                         f"NOTE: *This message is only sent one time, attempting to use buttons after receiving this will return with `` interaction failed ``*\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"),
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.homebase_long":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to change Homebase name to:\n"
                         f"```{truncate(acc_name)}```\n"
                         f"**This name is too long.**\n"
                         f"⦾ Homebase names must be under 16 characters\n"
                         f"⦾ Homebase names also have additional criteria, to check them, try running "
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"\u200b\n"),
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.homebase_illegal":
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to change Homebase name to:\n"
                         f"```{acc_name}```\n"
                         f"**This name contains unacceptable characters.**\n"
                         f"⦾ Homebase names must be alphanumeric, with limited support for extra characters.\n"
                         f"⦾ Homebase names also have additional criteria, to check them, try running "
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"\u200b\n"),
            colour=error_colour
        )

    else:
        embed = discord.Embed(
            title=await add_emoji_title(client, random_error(client), "error"),
            description=(f"\u200b\n"
                         f"Attempted to claim daily for account:\n"
                         f"```{acc_name}```\n"
                         f"**Unknown error received from epic games:**\n"
                         f"```{error_code}```\n"
                         f"You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)\n"
                         f"\u200b\n"
                         f"**If you need any help try:**\n"
                         f"{await mention_string(client, 'help {0}'.format(command))}\n"
                         f"Or [Join the support server]({support_url})\n"
                         f"Note: You need a new code __every time you authenticate__\n\u200b"),
            colour=error_colour
        )

    embed = await set_thumbnail(client, embed, error_level)
    embed = await add_requested_footer(ctx, embed)
    return embed


async def strip_string(string):
    """
    Strips a string of all non-alphanumeric characters

    Args:
        string: string to be stripped

    Returns:
        regex stripped string
    """
    return re.sub("[^0-9a-zA-Z]+", "", string)


def create_command_dict(client):
    """
    Creates a dictionary of all commands and their aliases

    Args:
        client: discord client

    Returns:
        a dictionary of command names, dictionary of commands, and list of command names
    """
    command_name_dict = {}
    command_dict = {}

    # Gets aliases and adds them to command_name_dict so we can match for aliases too in the command arg
    for command in client.commands:
        command_name_dict[command.name] = command.name
        for alias in command.aliases:
            command_name_dict[alias] = command.name

        # Adds the command to the 
        command_dict[command.name] = command

    return command_name_dict, command_dict, list(command_name_dict)


def extract_auth_code(string):
    """
    Extracts the auth code from a string

    Args:
        string: string to extract from

    Returns:
        The extracted auth code if possible, else an error code if the string is the correct length, finally just returns the string
    """
    try:
        return re.search(r"[0-9a-f]{32}", string)[0]  # hi

    except TypeError:
        if len(string) == 32:
            return "errors.stwdaily.illegal_auth_code"

        return string


async def is_legal_homebase_name(string):
    """
    Checks if a string is a legal homebase name

    Homebase names must be alphanumeric, with limited support for extra characters.

    Args:
        string: string to check

    Returns:
        True if legal, else False
    """
    # TODO: add obfuscated filter for protected homebase names
    return re.match(r"^[0-9a-zA-Z '\-._~]{1,16}$", string)


async def generate_banner(client, embed, homebase_icon, homebase_colour, author_id):
    """
    Generates a banner thumbnail for the embed

    Args:
        client: discord client
        embed: embed to add the banner to
        homebase_icon: homebase icon to use (e.g. ot7banner)
        homebase_colour: homebase colour to use (e.g. defaultcolor15)
        author_id: author id to use for the banner

    Returns:
        Embed with thumbnail set to the banner, discord attachment of file generated
    """
    banner_url = f"https://fortnite-api.com/images/banners/{homebase_icon}/icon.png"
    async with client.stw_session.get(banner_url) as resp:
        data = io.BytesIO(await resp.read())
        banner_screen = blendmodes.blend.blendLayers(Image.open(data).convert("RGB").resize((256, 256)),
                                                     Image.new("RGB", (256, 256),
                                                               await get_banner_colour(homebase_colour, "rgb")),
                                                     blendmodes.blend.BlendType.SCREEN)
        banner_texture = blendmodes.blend.blendLayers(banner_screen, banner_d, blendmodes.blend.BlendType.DIVIDE)
        banner_masked = blendmodes.blend.blendLayers(banner_texture, banner_m, blendmodes.blend.BlendType.DESTIN)
        att_img = io.BytesIO()
        banner_masked.save(att_img, format='PNG')
        att_img.seek(0)
        file = discord.File(att_img, filename=f"{author_id}banner.png")
    embed.set_thumbnail(url=f"attachment://{author_id}banner.png")
    return embed, file


async def research_stat_rating(stat, level):
    """
    Calculates the % stat buff given to player + team from a research level

    Args:
        stat: string of the stat (e.g. fortitude, offense, resistance, technology)
        level: level of the stat

    Returns:
        tuple: The combined rating of the stat, the personal rating, the team rating
    """
    personal_rating = get_rating(data_table=ResearchSystem, row=f"{stat}_personal_cumulative", time_input=level)
    team_rating = get_rating(data_table=ResearchSystem, row=f"{stat}_team_cumulative", time_input=level)
    return personal_rating + team_rating, personal_rating, team_rating


def research_stat_cost(stat, level):
    """
    Calculates the cost to upgrade a research stat
    I'm not sure if the level given is the current level, or the next level, assume the next level

    Args:
        stat: string of the stat (e.g. fortitude, offense, resistance, technology)
        level: current level of the stat

    Returns:
        tuple: The cost to upgrade the stat
    """
    return get_rating(data_table=ResearchSystem, row=f"{stat}_cost", time_input=sorted((0, level + 1, 120))[1])


def convert_iso_to_unix(iso_timestamp):
    """
    Converts an ISO timestamp to a unix timestamp rounded to the nearest second

    Args:
        iso_timestamp: ISO timestamp to convert

    Returns:
        unix timestamp rounded to the nearest second
    """
    return round(datetime.datetime.fromisoformat(iso_timestamp).timestamp())


def get_progress_bar(start, end, length):
    """
    Generates a progress bar

    Args:
        start: start of the progress bar
        end: end of the progress bar
        length: length of the progress bar

    Returns:
        progress bar string
    """
    return f"[{'=' * round((start / end) * length)}{'-' * (length - round((start / end) * length))}]"
